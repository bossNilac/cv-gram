from typing import List, Dict, Any

from pydantic import BaseModel, constr, EmailStr, Field
from pydantic.v1 import confloat

Score = confloat(ge=0.0)  # adjust bounds if you cap to 1.0 or 100.0
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
    profile_json: str

class MeOut(BaseModel):
    email: str
    is_Active: bool
    created_at: str
    updated_at: str

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