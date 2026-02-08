from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Integer,
    Text, UUID,
)
from sqlalchemy import MetaData
from sqlalchemy.dialects.oracle import TIMESTAMP
from sqlalchemy.dialects.postgresql import BYTEA, JSONB
from sqlalchemy.dialects.postgresql.base import DOUBLE_PRECISION
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Consistent constraint & index names (handy for migrations)
naming_convention = {
    "pk": "pk_%(table_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
}

metadata = MetaData(naming_convention=naming_convention)


class Base(DeclarativeBase):
    metadata = metadata

class Sessions(Base):
    __tablename__ = "sessions"
    id: Mapped[str] = mapped_column(UUID, primary_key=True)
    user_id: Mapped[str] = mapped_column(UUID, primary_key=True)
    token_hash: Mapped[bytes] = mapped_column(BYTEA, nullable=False)
    created_at: Mapped[str] = mapped_column(TIMESTAMP, nullable=False)
    expires_at: Mapped[str] = mapped_column(TIMESTAMP, nullable=False)
    revoked_at: Mapped[str] | None = mapped_column(TIMESTAMP, nullable=False)
    ip: Mapped[str] = mapped_column(Text, nullable=False)
    agent: Mapped[str] = mapped_column(Text, nullable=False)


class User(Base):
    __tablename__ = "users"
    uuid: Mapped[str] = mapped_column(UUID, primary_key=True)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    is_Active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[str] = mapped_column(TIMESTAMP, nullable=False)
    updated_at: Mapped[str] = mapped_column(TIMESTAMP, nullable=False)

class PasswordToken(Base):
    __tablename__ = "password_reset_tokens"
    id: Mapped[str] = mapped_column(UUID, primary_key=True)
    user_id: Mapped[str] = mapped_column(UUID, primary_key=True)
    token_hash: Mapped[bytes] = mapped_column(BYTEA, nullable=False)
    created_at: Mapped[str] = mapped_column(TIMESTAMP, nullable=False)
    expires_at: Mapped[str] = mapped_column(TIMESTAMP, nullable=False)
    used_at: Mapped[str] | None = mapped_column(TIMESTAMP, nullable=False)

class Profile(Base):
    __tablename__ = "profile"
    user_id: Mapped[str] = mapped_column(UUID, primary_key=True)

    overall_score: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)
    projects_score: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)
    experience_score: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)
    education_score: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)
    skills_score: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)
    profile_json: Mapped[str] = mapped_column(JSONB, nullable=False)

class EmailToken(Base):
    __tablename__ = "email_verification"
    id: Mapped[str] = mapped_column(UUID, primary_key=True)
    user_id: Mapped[str] = mapped_column(UUID, primary_key=True)
    token_hash: Mapped[bytes] = mapped_column(BYTEA, nullable=False)
    created_at: Mapped[str] = mapped_column(TIMESTAMP, nullable=False)
    expires_at: Mapped[str] = mapped_column(TIMESTAMP, nullable=False)
    used_at: Mapped[str] | None = mapped_column(TIMESTAMP, nullable=False)