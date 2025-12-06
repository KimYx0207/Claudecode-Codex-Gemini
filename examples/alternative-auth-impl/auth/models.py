"""SQLAlchemy ORM models for authentication.

This module defines the `User` and `RefreshToken` models and initializes
the SQLAlchemy engine/session for the application. Tables are created at
import time for convenience in simple deployments.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    """Base class for declarative SQLAlchemy models."""


settings = get_settings()

# Configure engine with SQLite-specific connect args when needed.
_connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, echo=False, future=True, connect_args=_connect_args)

# Session factory for dependency injection in FastAPI routes.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class User(Base):
    """User account model.

    Attributes:
        id: Primary key.
        email: Unique email address.
        username: Unique username.
        hashed_password: Bcrypt-hashed password.
        is_active: Active status flag.
        is_superuser: Superuser flag.
        created_at: Creation timestamp in UTC.
        refresh_tokens: Relationship to related refresh tokens.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class RefreshToken(Base):
    """Persisted refresh token for rotation and revocation.

    Attributes:
        id: Primary key.
        jti: Token unique identifier embedded in the JWT.
        token_hash: SHA-256 hash of the raw refresh token (not stored in plaintext).
        user_id: Foreign key to the user.
        revoked: Revocation flag.
        created_at: Creation timestamp in UTC.
        expires_at: Expiration timestamp in UTC.
        user: Relationship back to `User`.
    """

    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    jti: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    token_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped[User] = relationship("User", back_populates="refresh_tokens")


# Create tables if not exist (simple bootstrap for demo and local dev)
Base.metadata.create_all(bind=engine)

