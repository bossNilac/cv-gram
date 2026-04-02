import json
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.params import Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.db.db import get_session
from backend.services.limiter import limiter
from backend.models.classes import Profile
from backend.models.dto_classes import ResumeScoresIn, ResumeScoresOut, ProfileOut, SearchOut
from backend.routers.auth_routers.auth_router import get_user_id

router = APIRouter()

def _compute_overall(dto: ResumeScoresIn) -> float:
    if dto.overall_score is not None:
        return float(dto.overall_score)
    # simple average of the four components; tweak weights if needed
    return float(
        (dto.projects_score + dto.experience_score + dto.education_score + dto.skills_score) / 4.0
    )

def _serialize_scores(row: Profile) -> ResumeScoresOut:
    return ResumeScoresOut(
        user_id=str(row.user_id),
        overall_score=float(row.overall_score),
        projects_score=float(row.projects_score),
        experience_score=float(row.experience_score),
        education_score=float(row.education_score),
        skills_score=float(row.skills_score),
    )

def _serialize_profile(row: Profile) -> ProfileOut:
    profile_json = _normalize_profile_json(row.profile_json)

    return ProfileOut(
        user_id=str(row.user_id),
        overall_score=float(row.overall_score),
        projects_score=float(row.projects_score),
        experience_score=float(row.experience_score),
        education_score=float(row.education_score),
        skills_score=float(row.skills_score),
        profile_json=profile_json,
    )

def _normalize_profile_json(value: Any) -> dict | None:
    if value is None:
        return None

    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None

    if isinstance(value, dict):
        return value

    return None

def _search_profiles(
    db: Session,
    *,
    q_name: Optional[str] = None,
    q_location: Optional[str] = None,
    q_experience: Optional[str] = None,
    q_education: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    overall_min: Optional[float] = None,
    overall_max: Optional[float] = None,
    projects_min: Optional[float] = None,
    projects_max: Optional[float] = None,
    experience_min: Optional[float] = None,
    experience_max: Optional[float] = None,
    education_min: Optional[float] = None,
    education_max: Optional[float] = None,
    skills_min: Optional[float] = None,
    skills_max: Optional[float] = None,
):
    stmt = text("""
        SELECT *
        FROM public.search_profiles_v3(
            :q_name,
            :q_location,
            :q_experience,
            :q_education,
            :p_limit,
            :p_offset,
            :overall_min,
            :overall_max,
            :projects_min,
            :projects_max,
            :experience_min,
            :experience_max,
            :education_min,
            :education_max,
            :skills_min,
            :skills_max
        )
    """)

    rows = db.execute(
        stmt,
        {
            "q_name": q_name,
            "q_location": q_location,
            "q_experience": q_experience,
            "q_education": q_education,
            "p_limit": limit,
            "p_offset": offset,
            "overall_min": overall_min,
            "overall_max": overall_max,
            "projects_min": projects_min,
            "projects_max": projects_max,
            "experience_min": experience_min,
            "experience_max": experience_max,
            "education_min": education_min,
            "education_max": education_max,
            "skills_min": skills_min,
            "skills_max": skills_max,
        }
    ).mappings().all()

    return rows


@limiter.limit("5/minute")
@router.get("/resume-scores", response_model=ResumeScoresOut)
def get_resume_scores(
    request: Request,
    db: Session = Depends(get_session),
):
    """
    Return the resume scores for the authenticated user.
    """
    user_id = get_user_id(request, db)
    row = db.query(Profile).filter(Profile.user_id == user_id).first()

    if not row:
        raise HTTPException(status_code=404, detail="No resume scores found")

    return _serialize_scores(row)

@limiter.limit("5/minute")
@router.get("/resume-scores/{user_id}", response_model=ResumeScoresOut)
def get_resume_scores_by_id(
    user_id: str,
    request: Request,
    db: Session = Depends(get_session),
):
    """
    Return the resume scores for the given user_id.
    """
    get_user_id(request, db)
    row = db.query(Profile).filter(Profile.user_id == user_id).first()

    if not row:
        raise HTTPException(status_code=404, detail="No resume scores found")

    return _serialize_scores(row)

@router.get("/search/", response_model=List[SearchOut])
def search_profiles(
    request: Request,
    db: Session = Depends(get_session),

    # text fields
    q_name: Optional[str] = Query(default=None),
    q_location: Optional[str] = Query(default=None),
    q_experience: Optional[str] = Query(default=None),
    q_education: Optional[str] = Query(default=None),

    # paging
    limit: int = Query(default=10, ge=1, le=50),
    offset: int = Query(default=0, ge=0),

    # numeric filters
    overall_min: Optional[float] = Query(default=None),
    overall_max: Optional[float] = Query(default=None),
    projects_min: Optional[float] = Query(default=None),
    projects_max: Optional[float] = Query(default=None),
    experience_min: Optional[float] = Query(default=None),
    experience_max: Optional[float] = Query(default=None),
    education_min: Optional[float] = Query(default=None),
    education_max: Optional[float] = Query(default=None),
    skills_min: Optional[float] = Query(default=None),
    skills_max: Optional[float] = Query(default=None),
):
    get_user_id(request, db)

    rows = _search_profiles(
        db,
        q_name=q_name,
        q_location=q_location,
        q_experience=q_experience,
        q_education=q_education,
        limit=limit,
        offset=offset,
        overall_min=overall_min,
        overall_max=overall_max,
        projects_min=projects_min,
        projects_max=projects_max,
        experience_min=experience_min,
        experience_max=experience_max,
        education_min=education_min,
        education_max=education_max,
        skills_min=skills_min,
        skills_max=skills_max,
    )

    return [
        SearchOut(
            user_id=str(row["user_id"]),
            overall_score=float(row["overall_score"]),
            projects_score=float(row["projects_score"]),
            experience_score=float(row["experience_score"]),
            education_score=float(row["education_score"]),
            skills_score=float(row["skills_score"]),
            profile_json=_normalize_profile_json(row["profile_json"]),
            rank=float(row["rank"]) if row["rank"] is not None else 0.0,
        )
        for row in rows
    ]

@limiter.limit("5/minute")
@router.get("/me", response_model=ProfileOut)
def get_my_profile(
    request: Request,
    db: Session = Depends(get_session),
):
    user_id = get_user_id(request, db)
    row = db.query(Profile).filter(Profile.user_id == user_id).first()

    if not row:
        raise HTTPException(status_code=404, detail="No profile found")

    return _serialize_profile(row)

@limiter.limit("5/minute")
@router.get("/user/{user_id}", response_model=ProfileOut)
def get_profile_by_user_id(
    user_id: str,
    request: Request,
    db: Session = Depends(get_session),
):
    get_user_id(request, db)
    row = db.query(Profile).filter(Profile.user_id == user_id).first()

    if not row:
        raise HTTPException(status_code=404, detail="No profile found")

    return _serialize_profile(row)
