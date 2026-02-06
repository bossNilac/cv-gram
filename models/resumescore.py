from __future__ import annotations

from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION
from models.base import Base


class ResumeScores(Base):
    __tablename__ = "resume_scores"
    __table_args__ = (
        {"schema": "challenges_schema"},
    )

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    overall_score: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)
    projects_score: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)
    experience_score: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)
    education_score: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)
    skills_score: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)

    def __repr__(self) -> str:
        return (
            f"<ResumeScores user_id={self.user_id} "
            f"overall={self.overall_score} projects={self.projects_score} "
            f"experience={self.experience_score} education={self.education_score} "
            f"skills={self.skills_score}>"
        )
