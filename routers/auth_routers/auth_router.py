import datetime
import hashlib
import secrets
import uuid
from datetime import timedelta

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import APIRouter, Depends, HTTPException
from fastapi import Request
from sqlalchemy.orm import Session
from starlette.responses import Response

from db.db import get_session
from main import limiter
from models.classes import User, PasswordToken, EmailToken, Sessions
from models.dto_classes import *
from services.email import notify_password_reset, notify_new_login, notify_welcome

router = APIRouter()

# ----------------------------
# Config / helpers
# ----------------------------

def utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)

def _create_session(
    *,
    db,
    user_id: str,
    request,
    ttl_hours: int = 24,
):
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).digest()

    now = utcnow()
    expires_at = now + timedelta(hours=ttl_hours)

    session = Sessions(
        id=str(uuid.uuid4()),
        user_id=user_id,
        token_hash=token_hash,
        ip=request.client.host if request.client else None,
        agent=request.headers.get("user-agent"),
        revoked_at=None,
        expires_at=expires_at,
        created_at=now,
    )

    db.add(session)
    db.flush()

    return session,raw_token

def _create_token(*,
    db,
    user_id: str,
    ttl_hours: int = 6,
    model_type):
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).digest()

    now = utcnow()
    expires_at = now + timedelta(hours=ttl_hours)

    if model_type == 'email':
        token = EmailToken(
            id=str(uuid.uuid4()),
            user_id=user_id,
            token_hash=token_hash,
            used_at=None,
            expires_at=expires_at,
            created_at=now,
        )
    elif model_type == 'password':
        token = PasswordToken(
            id=str(uuid.uuid4()),
            user_id=user_id,
            token_hash=token_hash,
            used_at=None,
            expires_at=expires_at,
            created_at=now,
        )
    else:
        raise ValueError('Wrong model type')

    db.add(token)
    db.flush()

    return raw_token

def _check_active_session(request, db):
    now = utcnow()
    session_token = request.cookies.get("session")
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    session_token_hash = hashlib.sha256(session_token.encode()).digest()
    db_session = (db.query(Sessions).filter(Sessions.expires_at > now).filter(Sessions.revoked_at.is_(None))
                  .filter(Sessions.token_hash == session_token_hash).first())

    if not db_session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    else:
        return db_session

def get_user_id(request , db):
    session = _check_active_session(request, db)
    user = db.query(User).filter(User.uuid == session.user_id).first()
    if not user :
        raise HTTPException(status_code=401, detail="Not authenticated")
    if not user.is_Active:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user.uuid , session

def _get_user_id_from_email(db: Session, email: str) -> str | None:
    user = db.query(User).filter(User.email == email).first()
    return user.uuid if user else None

argon2_hasher = PasswordHasher()

def hash_password(plain: str) -> str:
    """Hash a plaintext password using Argon2id."""
    return argon2_hasher.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against an Argon2 hash."""
    try:
        return argon2_hasher.verify(hashed, plain)
    except VerifyMismatchError:
        return False

@limiter.limit("5/minute")
@router.post("/register", response_model=RegisterOut, status_code=201)
def register(request: Request,payload: RegisterIn, db: Session = Depends(get_session)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        uuid=str(uuid.uuid4()),
        email=payload.email,
        password_hash=hash_password(payload.password),
        created_at=utcnow(),
        updated_at=utcnow(),
        is_Active=False,
    )
    db.add(user)
    db.commit()

    token = _create_token(db=db,user_id=user.uuid,model_type='email')
    notify_welcome(user.email,token)

    return RegisterOut(email=user.email)

@limiter.limit("5/minute")
@router.post("/login")
def login(request: Request,payload: LoginIn, db: Session = Depends(get_session)):

    user = (
        db.query(User)
        .filter(
            (User.email == payload.email)
        )
        .first()
    )
    if not user :
        if (not user.is_Active
                or not verify_password(payload.password, str(user.password_hash))):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        raise HTTPException(status_code=401, detail="Invalid credentials")


    session = _create_session(db=db, user_id=str(user.uuid), request=request)
    db.commit()

    notify_new_login(email=user.email,when_text=utcnow(),device_text=request.client.host,reset_link='password/reset')
    response = Response(status_code=200, content="ok")
    response.set_cookie("session",session[1],#raw token
                        expires=session[0].expires_at,
                        path = "/",httponly = True,
                        secure = False,  samesite = "lax")
    return response


@limiter.limit("5/minute")
@router.post("/logout")
def logout(request: Request,db: Session = Depends(get_session)):

    db_session = _check_active_session(request, db)
    db_session.revoked_at = utcnow()
    db.commit()
    response = Response(status_code=200, content="ok")
    response.delete_cookie("session",path="/",
                        httponly = True,
                        secure = False,  samesite = "lax")
    return response

@limiter.limit("20/minute")
@router.post("/me")
def me(request: Request,db: Session = Depends(get_session)):
    # TODO upgrade this
    get_user_id(request, db)
    return Response(status_code=200, content="ok")

@limiter.limit("5/minute")
@router.post("/password/forgot")
def forgot(request: Request,payload:ResetRequestIn,
           db: Session = Depends(get_session)):

    _id = _get_user_id_from_email (db, payload.email)
    if not _id:
        return Response(status_code=200, content="ok")
    password_token = _create_token(db=db, user_id=_id,model_type='password')
    db.commit()
    notify_password_reset(payload.email,password_token)
    return Response(status_code=200, content="ok")

@limiter.limit("5/minute")
@router.post("/password/reset")
def forgot(payload:ResetPasswordIn,
           db: Session = Depends(get_session)):

    now = utcnow()
    password_token_hash = hashlib.sha256(payload.token.encode()).digest()
    db_token = (db.query(PasswordToken).filter(PasswordToken.expires_at > now).filter(PasswordToken.used_at.is_(None))
                  .filter(PasswordToken.token_hash == password_token_hash).first())
    if not db_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = db.query(User).filter(User.uuid == db_token.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user.password_hash = argon2_hasher.hash(payload.new_password)
    db_token.used_at = now
    (
        db.query(PasswordToken)
        .filter(PasswordToken.user_id == db_token.user_id)
        .filter(PasswordToken.used_at.is_(None))
        .update({PasswordToken.used_at: now}, synchronize_session=False)
    )
    (
        db.query(Sessions)
        .filter(Sessions.user_id == db_token.user_id)
        .filter(Sessions.revoked_at.is_(None))
        .update({Sessions.revoked_at: now}, synchronize_session=False)
    )
    db.commit()

    response = Response(status_code=200, content="ok")
    response.delete_cookie(
        "session",
        path="/",
        httponly=True,
        secure=False,
        samesite="lax",
    )
    return response

@limiter.limit("5/minute")
@router.post("/logout_all")
def logout(request: Request,db: Session = Depends(get_session)):

    user_id = get_user_id(request, db)[0]
    now = utcnow()
    (
        db.query(Sessions)
        .filter(Sessions.user_id == user_id)
        .filter(Sessions.revoked_at.is_(None))
        .update({Sessions.revoked_at: now}, synchronize_session=False)
    )
    db.commit()
    response = Response(status_code=200, content="ok")
    response.delete_cookie("session",path="/",
                        httponly = True,
                        secure = False,  samesite = "lax")
    return response

@limiter.limit("5/minute")
@router.delete("/sessions/{_id}")
def logout(_id,request: Request,db: Session = Depends(get_session)):

    user_id = get_user_id(request, db)[0]
    now = utcnow()
    session = _check_active_session(request, db)
    response = Response(status_code=200, content="ok")
    if session.id == _id:
        response.delete_cookie("session", path="/",
                               httponly=True,
                               secure=False, samesite="lax")
    (
        db.query(Sessions)
        .filter(Sessions.user_id == user_id)
        .filter(Sessions.id == _id)
        .filter(Sessions.revoked_at.is_(None))
        .update({Sessions.revoked_at: now}, synchronize_session=False)
    )
    db.commit()

    return response

@limiter.limit("5/minute")
@router.get("/sessions")
def get_sessions(request: Request,db: Session = Depends(get_session)):
    user_id = get_user_id(request, db)[0]
    now = utcnow()
    output = (
        db.query(Sessions)
        .filter(Sessions.user_id == user_id)
        .filter(Sessions.revoked_at.is_(None))
        .filter(Sessions.expires_at > now).all()
    )
    return output

@limiter.limit("5/minute")
@router.post("/verify-mail")
def verify(payload:VerifyEmailIn,request: Request,db: Session = Depends(get_session)):
    token_hash =hashlib.sha256(payload.token.encode()).digest()
    now = utcnow()
    token = (
        db.query(EmailToken)
        .filter(EmailToken.token_hash == token_hash)
        .filter(EmailToken.used_at.is_(None))
        .filter(EmailToken.expires_at > now)
        .first()
    )
    if not token:
        raise HTTPException(status_code=400, detail="Invalid token")

    token.used_at = utcnow()
    user = db.query(User).filter(User.uuid == token.user_id).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")
    user.is_Active = True
    db.commit()

    return Response(status_code=200, content="ok")




