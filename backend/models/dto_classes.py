from datetime import datetime
from typing import Dict, Any

from pydantic import BaseModel, constr, EmailStr, Field
from typing_extensions import Annotated

Score = Annotated[float, Field(ge=0, le=100)]
Password = constr(min_length=8, max_length=128)

class RegisterIn(BaseModel):
    email: EmailStr
    password: Password

class RegisterOut(BaseModel):
    email: EmailStr

class LoginIn(BaseModel):
    email: str = Field(..., description="email")
    password: str

class ResetRequestIn(BaseModel):
    email: EmailStr

class ResetPasswordIn(BaseModel):
    token : str
    new_password: Password

class VerifyEmailIn(BaseModel):
    token : str

class ResumeScoresOut(BaseModel):
    user_id: str
    overall_score: float
    projects_score: float
    experience_score: float
    education_score: float
    skills_score: float

class ProfileOut(BaseModel):
    user_id: str
    overall_score: float
    projects_score: float
    experience_score: float
    education_score: float
    skills_score: float
    profile_json: Dict[str, Any] | None

class SearchOut(BaseModel):
    user_id: str
    overall_score: float
    projects_score: float
    experience_score: float
    education_score: float
    skills_score: float
    profile_json: Dict[str, Any] | None
    rank: float

class MeOut(BaseModel):
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

class SessionOut(BaseModel):
    id: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    revoked_at: datetime | None
    ip: str | None
    agent: str | None

class ResumeScoresIn(BaseModel):
    # Require the 4 components; overall is optional (will compute if omitted)
    projects_score: Score = Field(..., description="Projects score")
    experience_score: Score = Field(..., description="Experience score")
    education_score: Score = Field(..., description="Education score")
    skills_score: Score = Field(..., description="Skills score")
    overall_score: Score | None = Field(
        None,
        description="If omitted, overall_score = average of component scores."
    )

class ScoreResponseModel(BaseModel):
    score: float = Field(..., description="Final score 0–100")
    parsed: Dict[str, Any]
