from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel, Field, confloat
from sqlalchemy.orm import Session

from db.db import get_session
from main import limiter
from models.classes import ResumeScores
from models.dto_classes import ResumeScoresIn, ResumeScoresOut

router = APIRouter()

def _compute_overall(dto: ResumeScoresIn) -> float:
    if dto.overall_score is not None:
        return float(dto.overall_score)
    # simple average of the four components; tweak weights if needed
    return float(
        (dto.projects_score + dto.experience_score + dto.education_score + dto.skills_score) / 4.0
    )

@limiter.limit("5/minute")
@router.get("/resume-scores", response_model=ResumeScoresOut)
def get_resume_scores(
    request: Request,
    db: Session = Depends(get_session),
):
    """
    Return the resume scores for the authenticated user.
    """
    user_id = int(getattr(request.state, "user_id", None))
    row = db.query(ResumeScores).filter(ResumeScores.user_id == user_id).first()

    if not row:
        raise HTTPException(status_code=404, detail="No resume scores found")

    return ResumeScoresOut(
        user_id=row.user_id,
        overall_score=float(row.overall_score),
        projects_score=float(row.projects_score),
        experience_score=float(row.experience_score),
        education_score=float(row.education_score),
        skills_score=float(row.skills_score),
    )

@limiter.limit("5/minute")
@router.get("/resume-scores/{user_id}", response_model=ResumeScoresOut)
def get_resume_scores_by_id(
    user_id: int,
    db: Session = Depends(get_session),
):
    """
    Return the resume scores for the given user_id.
    """
    row = db.query(ResumeScores).filter(ResumeScores.user_id == user_id).first()

    if not row:
        raise HTTPException(status_code=404, detail="No resume scores found")

    return ResumeScoresOut(
        user_id=row.user_id,
        overall_score=float(row.overall_score),
        projects_score=float(row.projects_score),
        experience_score=float(row.experience_score),
        education_score=float(row.education_score),
        skills_score=float(row.skills_score),
    )