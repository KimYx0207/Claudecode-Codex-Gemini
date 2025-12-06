"""FastAPI routes for JWT-based authentication.

Endpoints:
    - POST /api/v1/auth/register
    - POST /api/v1/auth/login
    - POST /api/v1/auth/refresh
    - POST /api/v1/auth/logout
    - GET /api/v1/auth/me
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth import schemas
from app.auth.dependencies import get_current_user, get_db
from app.auth.models import User
from app.auth.service import AuthService


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register_user(payload: schemas.RegisterRequest, db: Session = Depends(get_db)) -> schemas.UserOut:
    """Register a new user.

    Args:
        payload: Registration request containing email, username and password.
        db: SQLAlchemy session.

    Returns:
        The created user (public fields only).
    """

    service = AuthService()
    user = service.register_user(db, payload)
    return schemas.UserOut.model_validate(user)


@router.post("/login", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)) -> schemas.TokenResponse:
    """Login using username/email and password to obtain tokens.

    Args:
        payload: Login credentials.
        db: SQLAlchemy session.

    Returns:
        Access and refresh tokens with metadata.
    """

    service = AuthService()
    return service.login(db, payload)


@router.post("/refresh", response_model=schemas.TokenResponse)
def refresh(payload: schemas.RefreshRequest, db: Session = Depends(get_db)) -> schemas.TokenResponse:
    """Refresh tokens by rotating the refresh token.

    Args:
        payload: Refresh request containing the current refresh token.
        db: SQLAlchemy session.

    Returns:
        New access and refresh tokens.
    """

    service = AuthService()
    return service.refresh(db, payload.refresh_token)


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(payload: schemas.RefreshRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    """Logout by revoking the provided refresh token.

    Args:
        payload: Refresh token wrapper used for logout.
        db: SQLAlchemy session.

    Returns:
        A simple confirmation message.
    """

    service = AuthService()
    service.logout(db, payload.refresh_token)
    return {"detail": "Logged out"}


@router.get("/me", response_model=schemas.UserOut)
def get_me(current_user: User = Depends(get_current_user)) -> schemas.UserOut:
    """Retrieve the currently authenticated user using the access token.

    Args:
        current_user: User resolved from the Bearer access token.

    Returns:
        The current user's public profile.
    """

    return schemas.UserOut.model_validate(current_user)

