from typing import List

from pydantic import BaseModel, constr, EmailStr, Field

from models.classes import Sessions

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

