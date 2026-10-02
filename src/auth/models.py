"""ORM models for authentication domain.

Defines `User` and `RefreshToken` models using SQLAlchemy 2.0 declarative mapping.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class User(Base):
    """User account model.

    Attributes:
        id (str): UUID string primary key.
        email (str): Unique email address.
        username (str): Unique username.
        hashed_password (str): Bcrypt hashed password.
        is_active (bool): Whether the account is active.
        created_at (datetime): Timestamp of creation.
        refresh_tokens (list[RefreshToken]): Related refresh tokens.
    """

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class RefreshToken(Base):
    """Stored refresh token for session management and revocation.

    Attributes:
        id (str): UUID string primary key.
        token (str): The refresh token (JWT) value.
        user_id (str): Associated user ID.
        expires_at (datetime): Expiration timestamp (UTC).
        revoked (bool): Whether this token has been revoked.
        user (User | None): Related user entity.
    """

    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    token: Mapped[str] = mapped_column(Text, unique=True, nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relationship
    user: Mapped[User | None] = relationship(back_populates="refresh_tokens")
