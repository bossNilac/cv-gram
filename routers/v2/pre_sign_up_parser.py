# ---------- Pre-signup async parsing (no user id) ----------
import json, uuid, asyncio, time
from typing import Dict, Any
from tempfile import SpooledTemporaryFile

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from routers.v2.parser import get_openai_acc_client, ACC_TERMS_MODEL, PRIMARY_MODEL, get_openai_client, \
    score_resume_function

# Reuse your existing functions/clients/models (already defined in your file)
# from .parser import score_resume_function, get_openai_client, get_openai_acc_client, PRIMARY_MODEL, ACC_TERMS_MODEL

router = APIRouter()

# In-memory job registry (proc_id -> job data)
JOBS: Dict[str, Dict[str, Any]] = {}
JOB_TTL_SECONDS = 60 * 60  # keep finished jobs 1h

def _now() -> int:
    return int(time.time())

def _new_proc_id() -> str:
    return uuid.uuid4().hex  # simple, URL-safe enough

def _job_set(proc_id: str, **kv):
    job = JOBS.setdefault(proc_id, {})
    job.update(kv)

def _require_job(proc_id: str) -> Dict[str, Any]:
    job = JOBS.get(proc_id)
    if not job:
        raise HTTPException(status_code=404, detail="Process ID not found.")
    return job

def _clone_uploadfile_from_bytes(data: bytes, filename: str) -> UploadFile:
    """
    Build a fresh UploadFile from bytes so the background task can read/close it
    exactly like FastAPI would hand it to your parser.
    """
    spooled = SpooledTemporaryFile(max_size=len(data) + 1)
    spooled.write(data)
    spooled.seek(0)
    return UploadFile(filename=filename, file=spooled)

async def _run_score_job(proc_id: str, data: bytes, filename: str, *, acc: bool):
    """
    Background runner: calls your existing score function and stores status/result.
    """
    try:
        _job_set(proc_id, status="running", stage="starting", started_at=_now(), progress=5)

        up = _clone_uploadfile_from_bytes(data, filename)
        client = get_openai_acc_client() if acc else get_openai_client()
        model = ACC_TERMS_MODEL if acc else PRIMARY_MODEL

        _job_set(proc_id, stage="scoring", progress=35)

        resp: JSONResponse = await score_resume_function(up, client, model)
        result = json.loads(resp.body.decode("utf-8"))

        _job_set(
            proc_id,
            status="done",
            stage="done",
            progress=100,
            finished_at=_now(),
            result=result,
            expires_at=_now() + JOB_TTL_SECONDS,
        )
    except HTTPException as e:
        _job_set(
            proc_id,
            status="failed",
            stage="error",
            progress=100,
            finished_at=_now(),
            error={"status_code": e.status_code, "detail": e.detail},
            expires_at=_now() + JOB_TTL_SECONDS,
        )
    except Exception as e:
        _job_set(
            proc_id,
            status="failed",
            stage="error",
            progress=100,
            finished_at=_now(),
            error={"status_code": 500, "detail": str(e)},
            expires_at=_now() + JOB_TTL_SECONDS,
        )

def _gc_jobs():
    """Best-effort cleanup; call at route entry to keep memory tidy."""
    now = _now()
    to_del = [pid for pid, j in JOBS.items() if j.get("expires_at") and j["expires_at"] < now]
    for pid in to_del:
        JOBS.pop(pid, None)

# -------------------- ROUTES (no user id) --------------------

@router.post("/resume/acc/score_async")
async def score_resume_acc_start(file: UploadFile = File(...)):
    """
    Start async scoring on ACC models (no auth, pre-signup).
    Returns a proc_id immediately.
    """
    _gc_jobs()
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    data = await file.read()
    filename = file.filename or "resume"
    await file.close()

    proc_id = _new_proc_id()
    _job_set(proc_id, status="queued", stage="queued", progress=0, created_at=_now(), acc=True, filename=filename)

    asyncio.create_task(_run_score_job(proc_id, data, filename, acc=True))
    return JSONResponse({"proc_id": proc_id, "status": "queued"})

@router.get("/resume/task_status/{task_id}")
def score_get_task_status(task_id: str):
    """
    Poll job status by proc_id. Public (no user id).
    """
    _gc_jobs()
    job = _require_job(task_id)
    payload = {
        "proc_id": task_id,
        "status": job.get("status", "unknown"),
        "stage": job.get("stage"),
        "progress": job.get("progress", 0),
        "created_at": job.get("created_at"),
        "started_at": job.get("started_at"),
        "finished_at": job.get("finished_at"),
        "acc": job.get("acc", False),
        "filename": job.get("filename"),
    }
    return JSONResponse(payload)

@router.get("/resume/result/{task_id}")
def score_get_result(task_id: str):
    """
    Return final result by proc_id. 404 if not ready. Public (no user id).
    """
    _gc_jobs()
    job = _require_job(task_id)
    if job.get("status") != "done":
        raise HTTPException(status_code=404, detail="Result not ready")
    return JSONResponse(job["result"])

# curl -s -X POST "http://127.0.0.1:9000/v2/pre-parser/resume/acc/score_async" -F "file=@C:\Users\Calin\Downloads\cv.pdf"
# curl -s -X GET "http://127.0.0.1:9000/v2/pre-parser/resume/task_status/{proc_id}"
# curl -s -X GET "http://127.0.0.1:9000/v2/pre-parser/resume/result/{proc_id}"