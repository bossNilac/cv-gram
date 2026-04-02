"""
OpenAI-powered CV Rater (V2)

Changes per request:
- Final score is 0–100 (not mroutered to 0–15).
- CV detection is handled **only by OpenAI**. The service always uploads parsed text to the models, which decides if it's a CV.
  - If not, the models responds with `is_cv=false` and an `error` string.
  - The API then returns a 422 with that error message.
- Still validate file type and reject corrupted/unreadable files before sending to OpenAI.
- Files handled strictly in RAM.
- Output structure is detailed and consistent, with components, weights, confidence, explanation, etc.
- Prompts and rules are generalized, suitable for all industries.
"""
from __future__ import annotations

import asyncio
import io
import json
import os
import time
import uuid
from functools import partial
from tempfile import SpooledTemporaryFile
from typing import Any, Dict, Optional

import anyio
from fastapi import File, HTTPException, UploadFile, APIRouter
from fastapi.params import Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.requests import Request

from backend import config
from backend.db.db import get_session
from backend.services.limiter import limiter
from backend.models.classes import Profile
from backend.models.dto_classes import ScoreResponseModel
from backend.routers.auth_routers.auth_router import get_user_id

# --- Config ---
OPENAI_API_KEY = config.Settings.openai_api_key
#
OPENAI_ADV_API_KEY = config.Settings.openai_adv_api_key
CV_MAX_MB = config.Settings.cv_max_mb
CHUNK = config.Settings.chunk

PRIMARY_MODEL = config.Settings.primary_model
ESCALATION_MODEL = config.Settings.escalation_model

ADV_MODEL = config.Settings.adv_model

AUTO_ESCALATE = config.Settings.auto_escalate
MIN_CONFIDENCE = config.Settings.min_confidence
ALLOWED_EXTS = {".pdf", ".doc", ".docx"}

# --- Optional MIME sniffing ---
try:
    import magic  # type: ignore
    _HAS_MAGIC = True
except Exception:
    _HAS_MAGIC = False

_CLIENT = None
_CLIENT_ADV = None

def get_openai_client():
    global _CLIENT
    if _CLIENT is None:
        if not OPENAI_API_KEY:
            raise HTTPException(status_code=500, detail="Missing OPENAI_API_KEY")
        from openai import OpenAI
        _CLIENT = OpenAI(api_key=OPENAI_API_KEY)
    return _CLIENT

def get_openai_adv_client():
    global _CLIENT_ADV
    if _CLIENT_ADV is None:
        if not OPENAI_ADV_API_KEY:
            raise HTTPException(status_code=500, detail="Missing OPENAI_ADV_API_KEY")
        from openai import OpenAI
        _CLIENT_ADV = OpenAI(api_key=OPENAI_ADV_API_KEY)
    return _CLIENT_ADV

def _read_streaming_to_memory(upload: UploadFile, max_mb: float) -> bytes:
    max_bytes = int(max_mb * 1024 * 1024)
    buf = io.BytesIO()
    total = 0
    while True:
        chunk = upload.file.read(CHUNK)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise HTTPException(status_code=413, detail=f"File too large. Max {max_mb:.0f} MB.")
        buf.write(chunk)
    return buf.getvalue()


def _ext(filename: Optional[str]) -> str:
    if not filename:
        return ""
    return os.path.splitext(filename)[1].lower()


def extract_text_from_bytes(data: bytes, filename: str) -> str:
    ext = _ext(filename)
    if ext not in ALLOWED_EXTS:
        raise HTTPException(status_code=415, detail="Unsupported file type. Allowed: PDF, DOC, DOCX.")

    if _HAS_MAGIC:
        try:
            mime = magic.from_buffer(data[:4096], mime=True)
            if ext == ".pdf" and not mime.startswith("application/pdf"):
                raise HTTPException(status_code=422, detail="Corrupted or mislabelled PDF.")
            if ext in {".doc", ".docx"} and not (
                mime.endswith("msword") or "officedocument" in mime or "word" in mime
            ):
                pass
        except Exception:
            pass

    if ext == ".pdf":
        try:
            from pdfminer.high_level import extract_text
            return extract_text(io.BytesIO(data)) or ""
        except Exception:
            raise HTTPException(status_code=422, detail="Failed to parse PDF (file may be corrupted).")

    if ext == ".docx":
        try:
            import docx
            doc = docx.Document(io.BytesIO(data))
            return "\n".join(par.text for par in doc.paragraphs)
        except Exception:
            raise HTTPException(status_code=422, detail="Failed to parse DOCX (file may be corrupted).")

    if ext == ".doc":
        try:
            import textract  # type: ignore
            txt = textract.process(io.BytesIO(data))  # type: ignore[arg-type]
            return txt.decode("utf-8", errors="ignore")
        except Exception:
            raise HTTPException(
                status_code=501,
                detail="Legacy .doc requires textract/antiword. Please convert to PDF/DOCX.",
            )

    raise HTTPException(status_code=415, detail="Unsupported file type.")


DEFAULT_WEIGHTS = {
    "education": 0.15,
    "experience": 0.40,
    "skills": 0.20,
    "ai_signal": 0.10,
    "projects": 0.15,
}

SYSTEM_PROMPT_PARSING = (
    "You are a professional CV/Resume evaluator for all fields (business, arts, healthcare, trades, science, "
    "engineering, public sector, etc.). Read ONLY the provided document text.\n\n"
    "OUTPUT CONTRACT\n"
    "- If the document is NOT a CV/resume, return strictly: {\"is_cv\": false, \"error\": \"<brief reason>\"}.\n"
    "- If it IS a CV/resume, return strictly the JSON object with keys: is_cv=true and parsed={...} matching the schema. "
    "Use concise, factual language; no extra keys.\n\n"
    "CONSISTENCY REQUIREMENTS\n"
    "- You MUST compute component scores (0–100), then compute overall_score as the WEIGHTED SUM of those components. "
    "Normalize the provided weights to sum to 1 before use. Set parsed.overall_score to this number (clamped 0–100).\n"
    "- Use the exact keys for archetypes: top_archetype_matches = [{\"name\": \"...\", \"match_pct\": <number>}].\n"
    "- If a section is missing (e.g., no projects), score that component accordingly (often very low or 0) rather than guessing.\n"
    "- Confidence is 0.0–1.0 and should be LOWER when sections are missing, vague, or only self-assessed.\n"
)

RULESET_PARSING = r"""
HARSH SCORING RULES (0–100 per component; weighted overall). Only truly exceptional CVs should exceed 80 overall.

DEFINITIONS
- "Exceptional Flags" include: major-company or elite-lab experience (e.g., FAANG, NASA/ESA/CERN, DeepMind, OpenAI), patents or peer-reviewed publications, national/international awards, top-3% competitions (e.g., IOI/IMO/ICPC medals, Kaggle Grandmaster), founding a product with significant users/revenue, leading teams delivering widely used systems.

GLOBAL CAPS (apply after computing component scores)
- If no full-time professional role (internships/part-time only): OVERALL CAP = 65 (unless Exceptional Flags present -> 75).
- If total professional experience < 2 years: OVERALL CAP = 70 (unless Exceptional Flags present -> 78).
- To exceed OVERALL 80, candidate must satisfy at least TWO of:
  (A) Completed degree with distinction (or Master's/PhD) or equivalent prestige,
  (B) 3+ years of impactful full-time experience with quantified outcomes,
  (C) 2+ flagship projects with external impact (live users, revenue, publications, awards),
  (D) Leadership/ownership of a team/system of consequence.

EDUCATION (0–100)
- Completed degrees: PhD 90–100, Master's 82–90, Bachelor 72–82, Associate/Diploma 60–70.
- Ongoing programs capped at 62 until finished.
- High school alone ≤ 20.
- Recognized professional certifications (AWS/Azure/GCP, Cisco, PMP, CPA, medical boards, etc.): +6 to +10 each (cap +20).
- School/attendance/self-assessment certificates total ≤ +5.
- Prestige/awards/distinctions: +0–8.
- Clamp 0–100.

EXPERIENCE (0–100)
- Full-time roles score fully; internships/traineeships count at 50% value and each < 3 months caps at 48.
- Years → baseline: 
  0 yrs: 30, 1 yr: 45, 2 yrs: 58, 3 yrs: 68, 5 yrs: 78, 8 yrs: 86, 12 yrs: 92 (interpolate).
- Quantified impact (%, $, users, performance, scale): +2 each (cap +16).
- Leadership/ownership (led, architected, managed, P&L, on-call ownership): +2 each (cap +12).
- Repeated internships at the same org have diminishing returns: after first, -4 each.
- Recent relevant role within last 18 months: +6; otherwise -6.
- Clamp 0–100.

SKILLS (0–100)
- Evidence-weighted: verified by work, publications, code, certifications, or awards.
- Self-assessed frameworks (e.g., “Digital Competence”) cap Skills at 52 unless corroborated.
- Breadth without depth cap = 60.
- Depth (proven expert use or certification) adds +10–25 to the most relevant stack (cap overall 100).
- Outdated or generic office tools alone cap = 40.
- Clamp 0–100.

PROJECTS (0–100)
- No dedicated section → cap at 0
- Only academic mentions → cap 35.
- Each substantive project (clear goal + role + outcome) +8 up to 5 (cap +40).
- External proof (GitHub/live demo/publication/app store/production) +6 each (cap +18).
- Real-world impact (users, revenue, uptime/SLA, citations, awards, competition results) +5 each (cap +20).
- Ownership/leadership in projects +3 each (cap +12).
- To exceed 70: must include external proof AND impact.
- Clamp 0–100.

AI_SIGNAL (0–100)
- Measures alignment to role archetypes (analyst/engineer/researcher/manager, etc.) + trajectory.
- Strong alignment with limited track record cap = 65.
- Proven alignment with achievements can reach 80–90.
- Clamp 0–100.

OVERALL (0–100)
- Weighted sum using provided weights (default harsh weights). Clamp 0–100.
- Apply GLOBAL CAPS after computing the weighted sum.

CONFIDENCE (0.0–1.0)
- Lower confidence for missing sections, vague claims, self-assessment without proof, or OCR/format noise.
- Early-career or incomplete profiles typically < 0.70.

STRENGTHS & WEAKNESSES CONTRACT(REQUIRED)
- Always include exactly 3 strengths and exactly 3 weaknesses.
- Bullets must be factual, concise, ≤140 characters each.
- If evidence is weak, fill with low-signal items rather than omitting.

HIGHLIGHTS (REQUIRED)
- Provide 3 concise bullets capturing the most verifiable achievements or signals.
- Prefer quantified outcomes (%, $, users, scale), external proof , leadership/ownership, awards, elite orgs.
- Keep each bullet ≤140 characters; no emojis; start with a verb or fact; avoid restating section titles.

STRICTNESS
- Do not inflate scores for attendance-only education, self-assessed skills, or unsubstantiated claims.
- Reserve >80 overall for clearly exceptional profiles per rules above.
"""

SYSTEM_PROMPT_PARSING_MINI = """You are a STRICT CV evaluator.
Follow the schema EXACTLY. Output ONLY a valid JSON object.
If the document is not a CV/resume, output: {"is_cv": false, "error": "<brief reason>"}.
If it is a CV/resume, output: {"is_cv": true, "parsed": {...}} with ONLY the schema keys.
Never add keys. Never invent facts. If unsure, omit the field (or use 0 for numeric).

MATH CONTRACT
- Compute component scores first.
- Normalize weights to sum to 1.
- overall_pre_cap = education*w_edu + experience*w_exp + skills*w_sk + ai_signal*w_ai + projects*w_prj.
- overall_score = clamp(overall_pre_cap, 0, 100) THEN apply GLOBAL CAP as an UPPER BOUND ONLY:
  overall_score = min(overall_score, global_cap_if_any).
- Global caps NEVER increase scores and are NEVER used as a default value.
- Round overall_score only at the end to the nearest integer (0.5 rounds up).

ARCHETYPE CONTRACT
- Always include exactly 3 items in top_archetype_matches.
- Use ONLY names from the allowed list (see rules). If uncertain, choose the closest three with low match_pct values rather than omitting.
- Each item must have: {"name": "<ArchetypeName>", "match_pct": <0–100 number>}.

Return JSON only."""

RULESET_PARSING_MINI = r"""
Exceptional Flags: elite orgs (FAANG/DeepMind/OpenAI/NASA/ESA/CERN), patents/papers, major awards, top-3% comps, founded product with real users/revenue, led widely used systems.

EDUCATION
- PhD 90–100; MSc 82–90; BSc 72–82(only if completed);
- Determine status PER HIGHEST DEGREE MENTIONED:
  * "Completed" (has end year or words like Graduated, Awarded, Degree obtained) → use normal bands.
  * "Ongoing / In progress / Present / Current / Expected <year>" (no completion yet) → cap EDUCATION at 62.
  * "High school only" → ≤20.
- If multiple entries exist, score the strongest, but if ALL are ongoing, cap at 62.
- Attendance-only certificates or short courses cannot lift above 62 while the main degree is ongoing; their total boost ≤ +5.

EXAMPLES (ENFORCEMENT)
- "BSc Computer Science (2022–Present)" → EDUCATION ≤ 62 (not 72).
- "MSc expected 2026; BSc completed 2022" → treat BSc as completed (use normal bands); MSc ongoing does NOT exceed BSc by itself.
- "PhD (ABD), expected 2025, no prior completed degree" → EDUCATION ≤ 62.


EXPERIENCE
- Internships/traineeships count at 50%; <3 months cap 48.
- Years baseline: 0y:30, 1y:45, 2y:58, 3y:68, 5y:78, 8y:86, 12y:92 (interpolate).
- Quantified impact (+2 each, cap +16). Leadership/ownership (+2 each, cap +12).
- Repeated internships at same org: after first, −4 each.
- Recent relevant role in last 18 months +6; else −6. Clamp 0–100.

SKILLS
- Evidence-weighted (work/pubs/code/certs/awards). Self-assessed caps 52 unless corroborated.
- Breadth without depth cap 60. Depth (proven expert use/cert) +10–25 (cap 100).
- Only generic office tools cap 40. Clamp 0–100.

PROJECTS
- No section → 0. Only academic mentions cap 35.
- Substantive project (goal + role + outcome) +8 each up to 5 (cap +40).
- External proof (GitHub/live/publication/app store/production) +6 each (cap +18).
- Real impact (users/revenue/SLA/citations/awards/competitions) +5 each (cap +20).
- Ownership/leadership +3 each (cap +12). >70 requires external proof AND impact. Clamp 0–100.

ARCHETYPE MATCHING (REQUIRED)
- Always return exactly 3 archetypes in top_archetype_matches, sorted by match_pct desc.
- Use field specific job names
- match_pct is a number 0–100. If uncertain, use low values (e.g., 5–20) rather than omitting.

AI_SIGNAL CONTRACT
- ai_signal must never be 0 unless the CV is empty/invalid.
- Assign a baseline (10–20) for weak alignment; scale higher for stronger evidence.
- Clamp 0–100.

STRENGTHS & WEAKNESSES CONTRACT
- Always include exactly 3 strengths and exactly 3 weaknesses.
- Bullets must be factual, concise, ≤140 characters each.
- If evidence is weak, fill with low-signal items rather than omitting.

HIGHLIGHTS (REQUIRED)
- Provide 2-3 concise bullets capturing the most verifiable achievements or signals.
- Prefer quantified outcomes (%, $, users, scale), external proof (GitHub, live app, publication), leadership/ownership, awards, elite orgs.
- Keep each bullet ≤140 characters; no emojis; start with a verb or fact; avoid restating section titles.

CONFIDENCE
- 0.0–1.0. Lower for missing sections, vague claims, self-assessed, OCR noise.
"""


RESPONSE_SCHEMA_PARSING = {
    "name": "cv_rating_payload",
    "schema": {
        "type": "object",
        "properties": {
            "is_cv": {"type": "boolean"},
            "error": {"type": "string"},
            "parsed": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "skills": {"type": "array", "items": {"type": "string"}},
                    "overall_score": {"type": "number"},
                    "components": {
                        "type": "object",
                        "properties": {
                            "education": {"type": "number"},
                            "experience": {"type": "number"},
                            "skills": {"type": "number"},
                            "ai_signal": {"type": "number"},
                            "projects": {"type": "number"},
                        },
                        "required": ["education", "experience", "skills", "ai_signal", "projects"]
                    },
                    "weights": {"type": "object", "additionalProperties": {"type": "number"}},
                    "confidence": {"type": "number"},
                    "explanation": {
                        "type": "object",
                        "properties": {
                            "highlights": {"type": "array", "items": {"type": "string"}},
                            "top_archetype_matches": {"type": "array", "items": {"type": "object"}},
                            "notes": {
                                "type": "object",
                                "additionalProperties": False,   # <- ban any unlisted keys
                                "properties": {
                                    "strengths": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "minItems": 1
                                    },
                                    "weaknesses": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "minItems": 1
                                    }
                                },
                                "required": ["strengths", "weaknesses"]
                            },
                        },
                        "required": ["highlights", "top_archetype_matches", "notes"]
                    },
                },
                "required": ["name", "email", "skills", "overall_score", "components", "weights", "confidence", "explanation"]
            },
        },
        "required": ["is_cv"]
    }
}

SYSTEM_PROMPT_LINKEDIN = (
    "You are a professional CV/Resume normalizer. Read ONLY the provided document text.\n\n"
    "OUTPUT CONTRACT\n"
    "- If the document is NOT a CV/resume, return strictly: {\"is_cv\": false, \"error\": \"<brief reason>\"}.\n"
    "- If it IS a CV/resume, return strictly the JSON object with keys: is_cv=true and parsed={...} matching the schema. "
    "Use concise, factual language; no extra keys.\n\n"
    "CONSISTENCY REQUIREMENTS\n"
    "- Do NOT invent facts. If a value is unknown, omit the field (or use null for *_date fields).\n"
    "- Normalize dates: use YYYY-MM if month is present; otherwise use YYYY.\n"
    "- Split bullet-like text into arrays (achievements/highlights) where applicable.\n"
    "- Merge contiguous roles at the same company (combine achievements)."
)

LINKEDIN_PROFILE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "basics": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "full_name": {"type": "string"},
                "headline": {"type": "string"},
                "email": {"type": "string"},
                "phone": {"type": "string"},
                "location": {"type": "string"},
                "summary": {"type": "string"},
                "urls": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "linkedin": {"type": "string"},
                        "github": {"type": "string"},
                        "portfolio": {"type": "string"},
                        "website": {"type": "string"}
                    }
                }
            },
            "required": ["full_name"]
        },
        "experience": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "title": {"type": "string"},
                    "company": {"type": "string"},
                    "employment_type": {"type": "string"},
                    "location": {"type": "string"},
                    "start_date": {"type": "string"},         # YYYY or YYYY-MM
                    "end_date": {"type": ["string", "null"]}, # YYYY or YYYY-MM or null
                    "is_current": {"type": "boolean"},
                    "description": {"type": "string"},
                    "achievements": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["title", "company"]
            }
        },
        "education": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "school": {"type": "string"},
                    "degree": {"type": "string"},
                    "field_of_study": {"type": "string"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": ["string", "null"]},
                    "grade": {"type": "string"},
                    "activities": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["school"]
            }
        },
        "projects": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string"},
                    "role": {"type": "string"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": ["string", "null"]},
                    "url": {"type": "string"},
                    "description": {"type": "string"},
                    "highlights": {"type": "array", "items": {"type": "string"}},
                    "tech": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["name"]
            }
        },
        "skills": {"type": "array", "items": {"type": "string"}},
        "certifications": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string"},
                    "issuer": {"type": "string"},
                    "issue_date": {"type": "string"},       # YYYY or YYYY-MM
                    "credential_id": {"type": "string"},
                    "credential_url": {"type": "string"}
                },
                "required": ["name"]
            }
        },
        "languages": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string"},
                    "proficiency": {"type": "string"}        # e.g., Native, C1, B2
                },
                "required": ["name"]
            }
        },
        "publications": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "title": {"type": "string"},
                    "publisher": {"type": "string"},
                    "date": {"type": "string"},
                    "url": {"type": "string"},
                    "summary": {"type": "string"}
                },
                "required": ["title"]
            }
        },
        "honors_awards": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "title": {"type": "string"},
                    "issuer": {"type": "string"},
                    "date": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["title"]
            }
        },
        "volunteer": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "role": {"type": "string"},
                    "organization": {"type": "string"},
                    "cause": {"type": "string"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": ["string", "null"]},
                    "description": {"type": "string"}
                },
                "required": ["role", "organization"]
            }
        }
    },
    "required": ["basics"]
}

RESPONSE_SCHEMA_LINKEDIN = {
    "schema":{
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "is_cv": {"type": "boolean"},
        "error": {"type": "string"},
        "parsed": LINKEDIN_PROFILE_SCHEMA
    },
    "required": ["is_cv"]
    }
}

RULESET_LINKEDIN = """STRICT OUTPUT RULES
1) Output exactly ONE JSON object that validates against the provided schema. No prose, no code fences.
2) If not a CV/resume, return only: {"is_cv": false, "error": "<brief reason>"}.
3) If a CV/resume, set is_cv=true and fill parsed per schema; do NOT include any confidence field.
4) Dates: use YYYY-MM if month is present; otherwise YYYY. For ongoing roles, end_date=null and is_current=true.
5) Experience: title and company required; keep description <= 3 sentences; put bullet-like lines into achievements[].
6) Education: map programs; include school, optional degree/field_of_study; add dates if present.
7) Projects: use name + description; optional url, tech[], highlights[].
8) Skills: flat, deduplicated list of short terms; no self-ratings.
9) Only include sections that are evidenced in the text; never invent facts.
10) No extra keys anywhere (additionalProperties:false).
"""


router = APIRouter()

# ===Jobs implementation===

processes :Dict[str,str]= {}
JOBS: Dict[str, Dict[str, Any]] = {}
JOB_TTL_SECONDS = 60 * 60  # keep finished jobs for 1h

def _now() -> int:
    return int(time.time())

def _new_proc_id() -> str:
    # ULID would be nice; uuid4 is fine & built-in
    return uuid.uuid4().hex

def _clone_uploadfile_from_bytes(data: bytes, filename: str) -> UploadFile:
    """
    Make a fresh UploadFile from raw bytes so the background task can read & close it
    without affecting the original request file object.
    """
    spooled = SpooledTemporaryFile(max_size=len(data) + 1)
    spooled.write(data)
    spooled.seek(0)
    return UploadFile(filename=filename, file=spooled)

def _job_set(proc_id: str, **kv):
    job = JOBS.setdefault(proc_id, {})
    job.update(kv)

async def _run_score_job(proc_id: str, data: bytes, filename: str, *, adv: bool):
    """
    Background runner that calls your existing score function and records status/result.
    """
    try:
        _job_set(proc_id, status="running", stage="starting", started_at=_now(), progress=5)

        # Build a fresh UploadFile for your parser
        up = _clone_uploadfile_from_bytes(data, filename)

        client = get_openai_adv_client() if adv else get_openai_client()
        model = ADV_MODEL if adv else PRIMARY_MODEL

        _job_set(proc_id, stage="scoring", progress=35)
        resp: JSONResponse = await score_resume_function(up, client, model)

        # Your function returns JSONResponse; extract JSON body
        result = json.loads(resp.body.decode("utf-8"))

        _job_set(
            proc_id,
            status="done",
            stage="done",
            progress=100,
            finished_at=_now(),
            result=result,
        )
    except HTTPException as e:
        _job_set(
            proc_id,
            status="failed",
            stage="error",
            progress=100,
            finished_at=_now(),
            error={"status_code": e.status_code, "detail": e.detail},
        )
    except Exception as e:
        _job_set(
            proc_id,
            status="failed",
            stage="error",
            progress=100,
            finished_at=_now(),
            error={"status_code": 500, "detail": str(e)},
        )

def _require_job(proc_id: str) -> Dict[str, Any]:
    job = JOBS.get(proc_id)
    if not job:
        raise HTTPException(status_code=404, detail="Process ID not found.")
    return job

def _attach_user_process(user_id: str, proc_id: str):
    # You asked to maintain this mapping
    processes[user_id] = proc_id

# ====Model Helpers zone====

def _call_openai_model(system_prompt,response_schema,rule_set,client,text: str, weights: Dict[str, float], model: str) -> Dict[str, Any]:
    """
    Version-tolerant call that uses Chat Completions with JSON mode.
    Works on older 1.x SDKs that don't support the Responses API args.
    """

    # Put schema + rules into the system message so JSON is enforced by instruction
    schema_text = json.dumps(response_schema["schema"])
    sys_msg = (
            system_prompt
            + "\n\nSCHEMA (strict, no extra keys):\n"
            + schema_text
            + "\n\nRULES:\n"
            + rule_set
            + "\n\nReturn ONLY valid JSON per the schema."
    )
    user_msg = (
        "RESUME TEXT BEGIN\n" + text.strip() + "\nRESUME TEXT END\n\n"
        "WEIGHTS JSON:\n" + json.dumps(weights)
    )

    messages = [
        {"role": "system", "content": sys_msg},
        {"role": "user",   "content": user_msg},
    ]

    # Try JSON mode (works on >= 1.2+ typically). If SDK/models rejects the kwarg,
    # call again without it and rely on strict prompting.
    try:
        if client is _CLIENT:
            resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2,
            response_format={"type": "json_object"},  # JSON mode
        )
        elif client is _CLIENT_ADV:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                response_format={"type": "json_object"},  # JSON mode
            )

    except TypeError:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2,
        )

    # Parse JSON safely
    try:
        content = resp.choices[0].message.content  # type: ignore[attr-defined]
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"OpenAI response missing content: {e}")

    try:
        return json.loads(content)
    except Exception as e:
        # Helpful error snippet for debugging
        snippet = content[:400].replace("\n", " ")
        raise HTTPException(status_code=502, detail=f"Failed to parse models JSON: {e}; snippet={snippet!r}")

async def score_resume_function(
            file,
            client,
            model,
            store: bool = False,
            user_id:str = None,
            db: Optional[Session] = None,
    ):

    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    ext = _ext(file.filename)
    if ext not in ALLOWED_EXTS:
        raise HTTPException(status_code=415, detail="Unsupported file type. Allowed: PDF, DOC, DOCX.")

    try:
        data = _read_streaming_to_memory(file, CV_MAX_MB)
    finally:
        try:
            await file.close()
        except Exception:
            pass

    text = extract_text_from_bytes(data, file.filename or "resume")
    if not text.strip():
        raise HTTPException(status_code=422, detail="Empty or unreadable document (OCR may be required).")

    weights = DEFAULT_WEIGHTS.copy()

    if model == "gpt-4o-mini":
        result = await _call_openai_model_async(SYSTEM_PROMPT_PARSING_MINI, RESPONSE_SCHEMA_PARSING
                                                , RULESET_PARSING_MINI, client, text, weights, model)
    else :
    # PRIMARY (off the event loop)
        result = await _call_openai_model_async(SYSTEM_PROMPT_PARSING,RESPONSE_SCHEMA_PARSING
                                            ,RULESET_PARSING,client, text, weights, model)

    if not result.get("is_cv"):
        reason = result.get("error") or "Provided file does not resemble a CV/resume."
        raise HTTPException(status_code=422, detail=reason)

    parsed = result.get("parsed") or {}
    conf = float(parsed.get("confidence") or 0.0)

    # ESCALATION (also off the event loop)
    if AUTO_ESCALATE and conf < MIN_CONFIDENCE and (model != ADV_MODEL):
        try:
            result_hi = await _call_openai_model_async(SYSTEM_PROMPT_PARSING,RESPONSE_SCHEMA_PARSING
                                            ,RULESET_PARSING,client, text, weights, ESCALATION_MODEL)
            if result_hi.get("is_cv"):
                parsed = result_hi.get("parsed") or parsed
        except Exception:
            pass


    # then apply caps as an upper bound if needed

    comps = parsed.get("components") or {}
    for k in ["education", "experience", "skills", "ai_signal", "projects"]:
        comps.setdefault(k, 0.0)
    parsed["components"] = comps

    # Calculate overall score after all components are set
    overall = sum(comps.get(k, 0.0) * weights.get(k, 0.0) for k in weights)
    overall = min(100, max(0, overall))  # clamp

    if store:
            row =  db.query(Profile).filter(Profile.user_id == user_id).first()
            # compute component scores safely
            education = float(comps.get("education", 0.0))
            experience = float(comps.get("experience", 0.0))
            skills = float(comps.get("skills", 0.0))
            projects = float(comps.get("projects", 0.0))

            if row:
                row.overall_score = overall
                row.education_score = education
                row.experience_score = experience
                row.skills_score = skills
                row.projects_score = projects
            else:
                new_row = Profile(
                    user_id=user_id,
                    overall_score=overall,
                    education_score=education,
                    experience_score=experience,
                    skills_score=skills,
                    projects_score=projects,
                    profile_json= None
                )
                db.add(new_row)
            db.commit()

    payload = {"score": overall, "parsed": parsed}
    return JSONResponse(content=json.loads(json.dumps(payload, ensure_ascii=False)))

async def linkedin_resume_function(file, client, model):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    ext = _ext(file.filename)
    if ext not in ALLOWED_EXTS:
        raise HTTPException(status_code=415, detail="Unsupported file type. Allowed: PDF, DOC, DOCX.")

    try:
        data = _read_streaming_to_memory(file, CV_MAX_MB)
    finally:
        try:
            await file.close()
        except Exception:
            pass

    text = extract_text_from_bytes(data, file.filename or "resume")
    if not text.strip():
        raise HTTPException(status_code=422, detail="Empty or unreadable document (OCR may be required).")


    # PRIMARY (off the event loop)
    result = await _call_openai_model_async(SYSTEM_PROMPT_LINKEDIN,RESPONSE_SCHEMA_LINKEDIN
                                            ,RULESET_LINKEDIN,client, text, {}, model)

    if not result.get("is_cv"):
        reason = result.get("error") or "Provided file does not resemble a CV/resume."
        raise HTTPException(status_code=422, detail=reason)

    parsed = result.get("parsed") or {}
    payload = {"profile": parsed}
    return payload

def _call_openai_model_sync(prompt,response,ruleset,client, text, weights, model) -> Dict[str, Any]:
    # your current blocking implementation lives here
    return _call_openai_model(prompt,response,ruleset,client, text, weights, model)

async def _call_openai_model_async(prompt,response,ruleset,client, text, weights, model) -> Dict[str, Any]:
    return await anyio.to_thread.run_sync(
        partial(_call_openai_model_sync, prompt,response,ruleset,client, text, weights, model)
    )

@router.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "openai_key": bool(OPENAI_API_KEY),
        "primary_model": PRIMARY_MODEL,
        "escalation_model": ESCALATION_MODEL,
        "auto_escalate": AUTO_ESCALATE,
        "min_confidence": MIN_CONFIDENCE,
        "max_mb": CV_MAX_MB,
    }

@router.get("/adv/health")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "openai_key": bool(OPENAI_ADV_API_KEY),
        "primary_model": ADV_MODEL,
        "auto_escalate": "No",
        "min_confidence": "Not needed",
        "max_mb": CV_MAX_MB,
    }

@limiter.limit("2/hour")
@router.post("/resume/score", response_model=ScoreResponseModel)
async def score_resume(request : Request,file: UploadFile = File(...),db: Session = Depends(get_session)):
    get_user_id(request,db)
    return await score_resume_function(file, get_openai_client(), PRIMARY_MODEL)

@router.put("/resume/score", response_model=ScoreResponseModel)
async def score_resume(request : Request,file: UploadFile = File(...),db: Session = Depends(get_session)):
    user_id = get_user_id(request,db)
    return await score_resume_function(file, get_openai_client(), PRIMARY_MODEL,True,user_id,db)

@limiter.limit("2/hour")
@router.post("/resume/adv/score_async")
async def score_resume_adv_start(request : Request,file: UploadFile = File(...),db: Session = Depends(get_session)):
    """
    Start async scoring on ADV models. Returns proc_id immediately.
    """
    user_id = get_user_id(request,db)

    data = await file.read()
    filename = file.filename or "resume"
    await file.close()

    proc_id = _new_proc_id()
    _job_set(proc_id, status="queued", stage="queued", progress=0, created_at=_now(), adv=True, filename=filename)
    _attach_user_process(user_id, proc_id)

    asyncio.create_task(_run_score_job(proc_id, data, filename, adv=True))

    return JSONResponse({"proc_id": proc_id, "status": "queued"})

@limiter.limit("2/hour")
@router.get("/resume/task_status/{task_id}")
def score_get_task_status(task_id: str, request: Request,db: Session = Depends(get_session)):
    """
    Poll job status by proc_id.
    """
    user_id = get_user_id(request, db)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    job = _require_job(task_id)

    if processes.get(user_id) != task_id:
        raise HTTPException(status_code=403, detail="Not allowed for this process id.")

    payload = {
        "proc_id": task_id,
        "status": job.get("status", "unknown"),
        "stage": job.get("stage"),
        "progress": job.get("progress", 0),
        "created_at": job.get("created_at"),
        "started_at": job.get("started_at"),
        "finished_at": job.get("finished_at"),
        "adv": job.get("adv", False),
        "filename": job.get("filename"),
        # You can include partials here later if you produce them
    }
    return JSONResponse(payload)

@limiter.limit("2/hour")
@router.get("/resume/result/{task_id}")
def score_get_result(task_id: str, request: Request,db: Session = Depends(get_session)):
    """
    Return final result by proc_id. 404 if not ready.
    """
    user_id = get_user_id(request, db)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    job = _require_job(task_id)

    if job.get("status") != "done":
        raise HTTPException(status_code=404, detail="Result not ready")

    # Return the exact shape your score function returns (score + parsed)
    return JSONResponse(job["result"])

@limiter.limit("2/hour")
@router.post("/resume/cv", response_model=ScoreResponseModel)
async def cv(request:Request ,file: UploadFile = File(...),db: Session = Depends(get_session)):
     user_id = get_user_id(request,db)
     profile = db.query(Profile).filter(Profile.user_id == user_id).first()
     payload = await linkedin_resume_function(file, get_openai_client(), PRIMARY_MODEL)
     if profile:
         profile.profile_json = payload
     db.commit()
     return JSONResponse(content=json.loads(json.dumps(payload, ensure_ascii=False)))


# curl -s -X POST "http://127.0.0.1:9000/v2/parser/resume/score" -F "file=@C:\Users\Calin\Downloads\cv.pdf"
# curl -s -X POST "http://127.0.0.1:9000/v2/parser/resume/adv/score" -F "file=@C:\Users\Calin\Downloads\cv.pdf"
# curl -s -X POST "http://127.0.0.1:9000/v2/parser/resume/cv" -F "file=@C:\Users\Calin\Downloads\cv.pdf"
# curl -s -X PUT "http://127.0.0.1:8000/v2/parser/resume/score" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI5ZTI4NTJhOS00Njc5LTQzNDQtODczNC1lZWQ3NTliNjQ2ZGQiLCJzdWIiOiIxIiwiaWF0IjoxNzYwMjk4MDEyLCJleHAiOjE3NjAzODQ0MTJ9.TtkNEKVgYiFPTvvZiXwyLJoejsweWxeDATH-3-TCsds" -F "file=@C:\Users\Calin\Downloads\cv.pdf"

# curl -X GET "http://127.0.0.1:8000/v1/resume-scores" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI5ZTI4NTJhOS00Njc5LTQzNDQtODczNC1lZWQ3NTliNjQ2ZGQiLCJzdWIiOiIxIiwiaWF0IjoxNzYwMjk4MDEyLCJleHAiOjE3NjAzODQ0MTJ9.TtkNEKVgYiFPTvvZiXwyLJoejsweWxeDATH-3-TCsds"

# curl -s -X POST "https://elite-chal-xp-tasks-fea8332d31e3.herokuapp.com/v2/parser/resume/score" -F "file=@C:\Users\Calin\Downloads\cv.pdf"
# curl -s -X POST "https://elite-chal-xp-tasks-fea8332d31e3.herokuapp.com/v2/parser/resume/adv/score" -F "file=@C:\Users\Calin\Downloads\cv.pdf"

skeleton_response_linkdin= {
  "profile": {
    "basics": {
      "full_name": "",
      "headline": "",
      "email": "",
      "phone": "",
      "location": "",
      "summary": "",
      "urls": {
        "linkedin": "",
        "github": "",
        "portfolio": "",
        "website": ""
      }
    },
    "experience": [
      {
        "title": "",
        "company": "",
        "employment_type": "",
        "location": "",
        "start_date": "",
        # "end_date": null,
        # "is_current": false,
        "description": "",
        "achievements": []
      }
    ],
    "education": [
      {
        "school": "",
        "degree": "",
        "field_of_study": "",
        "start_date": "",
        # "end_date": null,
        "grade": "",
        "activities": "",
        "description": ""
      }
    ],
    "projects": [
      {
        "name": "",
        "role": "",
        "start_date": "",
        # "end_date": null,
        "url": "",
        "description": "",
        "highlights": [],
        "tech": []
      }
    ],
    "skills": [],
    "certifications": [
      {
        "name": "",
        "issuer": "",
        "issue_date": "",
        "credential_id": "",
        "credential_url": ""
      }
    ],
    "languages": [
      {
        "name": "",
        "proficiency": ""
      }
    ],
    "publications": [
      {
        "title": "",
        "publisher": "",
        "date": "",
        "url": "",
        "summary": ""
      }
    ],
    "honors_awards": [
      {
        "title": "",
        "issuer": "",
        "date": "",
        "description": ""
      }
    ],
    "volunteer": [
      {
        "role": "",
        "organization": "",
        "cause": "",
        "start_date": "",
        # "end_date": null,
        "description": ""
      }
    ]
  }
}

skeleton_response_parsing={
  "score": 0,
  "parsed": {
    "name": "",
    "email": "",
    "skills": [],
    "overall_score": 0,
    "components": {
      "education": 0,
      "experience": 0,
      "skills": 0,
      "ai_signal": 0,
      "projects": 0
    },
    "weights": {
      "education": 0,
      "experience": 0,
      "skills": 0,
      "ai_signal": 0,
      "projects": 0
    },
    "confidence": 0,
    "explanation": {
      "highlights": [],
      "top_archetype_matches": [
        { "name": "", "match_pct": 0 }
      ],
      "component_details": {
        "education": "",
        "experience": "",
        "skills": "",
        "ai_signal": "",
        "projects": ""
      },
      "notes": {
        "strengths": [],
        "weaknesses": []
      }
    }
  }
}
