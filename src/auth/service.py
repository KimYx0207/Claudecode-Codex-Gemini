"""Authentication service layer with business logic.

Provides user registration, authentication, token issuance and refresh handling.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from fastapi import HTTPException, status
from sqlalchemy import or_, select

from src.auth.models import RefreshToken, User
from src.auth.utils import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.auth.schemas import UserRegisterRequest


async def register_user(db: AsyncSession, user_data: UserRegisterRequest) -> User:
    """Register a new user account.

    Args:
        db (AsyncSession): Database session.
        user_data (UserRegisterRequest): Registration payload with email, username, password.

    Returns:
        User: The created user entity.

    Raises:
        HTTPException: If email or username is already registered.
    """

    existing_stmt = select(User).where(
        or_(User.email == user_data.email, User.username == user_data.username)
    )
    result = await db.execute(existing_stmt)
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered",
        )

    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    """Authenticate a user by email and password.

    Args:
        db (AsyncSession): Database session.
        email (str): User email.
        password (str): Plain password.

    Returns:
        User: The authenticated user.

    Raises:
        HTTPException: If credentials are invalid or user is inactive.
    """

    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user account")
    return user


def create_tokens(user: User) -> tuple[str, str]:
    """Create access and refresh JWT tokens for a user.

    Note: Persistence of refresh tokens is handled by the caller.

    Args:
        user (User): The user for whom to generate tokens.

    Returns:
        Tuple[str, str]: (access_token, refresh_token)
    """

    access_token = create_access_token({"sub": user.id, "email": user.email})
    refresh_token = create_refresh_token({"sub": user.id, "email": user.email})
    return access_token, refresh_token


async def refresh_access_token(db: AsyncSession, refresh_token: str) -> tuple[str, str]:
    """Issue a new access token using a valid refresh token.

    Verifies the provided refresh token against the database for revocation and
    expiration, then issues a new access token. For simplicity, the refresh
    token is re-used until it expires.

    Args:
        db (AsyncSession): Database session.
        refresh_token (str): The refresh token.

    Returns:
        Tuple[str, str]: (access_token, refresh_token). The refresh token is unchanged.

    Raises:
        HTTPException: If the refresh token is invalid, revoked, or expired.
    """

    # Lookup refresh token in DB
    stmt = select(RefreshToken).where(RefreshToken.token == refresh_token)
    result = await db.execute(stmt)
    stored = result.scalar_one_or_none()
    if not stored or stored.revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )
    if stored.expires_at <= datetime.now(UTC):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired"
        )

    # Fetch the user to embed claims
    user_stmt = select(User).where(User.id == stored.user_id)
    user_res = await db.execute(user_stmt)
    user = user_res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")

    new_access_token = create_access_token({"sub": user.id, "email": user.email})
    return new_access_token, refresh_token


async def revoke_refresh_token(db: AsyncSession, token: str) -> None:
    """Revoke a specific refresh token.

    Args:
        db (AsyncSession): Database session.
        token (str): Refresh token string to revoke.

    Raises:
        HTTPException: If token not found.
    """

    stmt = select(RefreshToken).where(RefreshToken.token == token)
    result = await db.execute(stmt)
    stored = result.scalar_one_or_none()
    if not stored:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Refresh token not found")
    stored.revoked = True
    db.add(stored)
    await db.commit()
