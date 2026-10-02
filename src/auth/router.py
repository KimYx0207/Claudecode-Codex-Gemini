"""Authentication API routes using FastAPI.

Endpoints:
    - POST /register
    - POST /login
    - POST /refresh
    - GET /me
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.auth.models import RefreshToken, User
from src.auth.schemas import (
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from src.auth.service import authenticate_user, create_tokens, refresh_access_token, register_user
from src.core.config import settings
from src.core.database import get_db

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_endpoint(
    payload: UserRegisterRequest, db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Register a new user.

    Args:
        payload (UserRegisterRequest): Registration data.
        db (AsyncSession): Database session dependency.

    Returns:
        UserResponse: The created user data.
    """

    user = await register_user(db, payload)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login_endpoint(
    payload: UserLoginRequest, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """Authenticate and issue tokens.

    Args:
        payload (UserLoginRequest): Login credentials.
        db (AsyncSession): Database session dependency.

    Returns:
        TokenResponse: Access and refresh tokens with expiry info.
    """

    user = await authenticate_user(db, payload.email, payload.password)
    access_token, refresh_token = create_tokens(user)

    # Persist refresh token for revocation tracking
    expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    db.add(RefreshToken(token=refresh_token, user_id=user.id, expires_at=expires_at, revoked=False))
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_endpoint(
    payload: RefreshTokenRequest, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """Issue a new access token using a refresh token.

    Args:
        payload (RefreshTokenRequest): Refresh token wrapper.
        db (AsyncSession): Database session dependency.

    Returns:
        TokenResponse: New access token and (same) refresh token.
    """

    new_access, refresh = await refresh_access_token(db, payload.refresh_token)
    return TokenResponse(
        access_token=new_access,
        refresh_token=refresh,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/me", response_model=UserResponse)
async def me_endpoint(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Retrieve current authenticated user profile."""

    return UserResponse.model_validate(current_user)
