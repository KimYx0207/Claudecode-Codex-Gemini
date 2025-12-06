"""Authentication service implementing business logic.

This module provides a service layer for registration, login, refresh,
logout, and current user resolution. It uses SQLAlchemy sessions and
utilities from `utils` for JWT and password operations.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.auth import schemas
from app.auth.models import RefreshToken, User
from app.auth.utils import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    hash_token,
    verify_password,
)


class AuthService:
    """Service providing core authentication operations."""

    def register_user(self, db: Session, data: schemas.RegisterRequest) -> User:
        """Register a new user with a unique email and username.

        Args:
            db: SQLAlchemy session.
            data: Registration payload.

        Returns:
            The created `User` instance.

        Raises:
            HTTPException: If email or username already exists.
        """

        # Check for existing user by email or username.
        existing = db.execute(
            select(User).where(or_(User.email == data.email, User.username == data.username))
        ).scalar_one_or_none()
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or username already registered",
            )

        user = User(
            email=data.email,
            username=data.username,
            hashed_password=get_password_hash(data.password),
            is_active=True,
            is_superuser=False,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def authenticate_user(self, db: Session, username_or_email: str, password: str) -> Optional[User]:
        """Authenticate a user by username or email and password.

        Args:
            db: SQLAlchemy session.
            username_or_email: Username or email identifier.
            password: Plaintext password.

        Returns:
            The authenticated `User` or None if authentication fails.
        """

        user = db.execute(
            select(User).where(or_(User.username == username_or_email, User.email == username_or_email))
        ).scalar_one_or_none()
        if user is None:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user

    def login(self, db: Session, data: schemas.LoginRequest) -> schemas.TokenResponse:
        """Perform user login and return access/refresh tokens.

        Args:
            db: SQLAlchemy session.
            data: Login payload with credentials.

        Returns:
            Token pair wrapped in `TokenResponse`.

        Raises:
            HTTPException: If credentials are invalid.
        """

        user = self.authenticate_user(db, data.username_or_email, data.password)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        settings = get_settings()
        access_token = create_access_token(user.id, settings)
        refresh_token, jti, expires_at = create_refresh_token(user.id, settings)

        db.add(
            RefreshToken(
                jti=jti,
                token_hash=hash_token(refresh_token),
                user_id=user.id,
                expires_at=expires_at,
                revoked=False,
            )
        )
        db.commit()

        return schemas.TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    def refresh(self, db: Session, refresh_token: str) -> schemas.TokenResponse:
        """Refresh token pair by rotating the refresh token.

        Args:
            db: SQLAlchemy session.
            refresh_token: Raw refresh token provided by the client.

        Returns:
            New token pair wrapped in `TokenResponse`.

        Raises:
            HTTPException: If the refresh token is invalid or revoked.
        """

        settings = get_settings()
        try:
            payload = decode_token(refresh_token, settings)
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token type")

        user_id = int(payload.get("sub"))
        jti = payload.get("jti")
        if not jti:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        token_record = db.execute(
            select(RefreshToken).where(RefreshToken.jti == jti, RefreshToken.user_id == user_id)
        ).scalar_one_or_none()

        if token_record is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found")

        if token_record.revoked:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked")

        if token_record.expires_at <= datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

        if token_record.token_hash != hash_token(refresh_token):
            # Token mismatch (e.g., reuse attempt); revoke it.
            token_record.revoked = True
            db.commit()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        # Rotate: revoke old token and issue a new one
        token_record.revoked = True
        db.commit()

        access_token = create_access_token(user_id, settings)
        new_refresh, new_jti, new_exp = create_refresh_token(user_id, settings)
        db.add(
            RefreshToken(
                jti=new_jti,
                token_hash=hash_token(new_refresh),
                user_id=user_id,
                expires_at=new_exp,
                revoked=False,
            )
        )
        db.commit()

        return schemas.TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    def logout(self, db: Session, refresh_token: str) -> None:
        """Logout by revoking the provided refresh token.

        Args:
            db: SQLAlchemy session.
            refresh_token: Raw refresh token string.
        """

        try:
            payload = decode_token(refresh_token)
        except Exception:
            # If the token isn't decodeable, it's effectively unusable; treat as already logged out.
            return

        jti = payload.get("jti")
        sub = payload.get("sub")
        if not jti or not sub:
            return

        token_record = db.execute(
            select(RefreshToken).where(RefreshToken.jti == jti, RefreshToken.user_id == int(sub))
        ).scalar_one_or_none()
        if token_record is None:
            return

        if not token_record.revoked:
            token_record.revoked = True
            db.commit()

    def get_user_from_access_token(self, db: Session, token: str) -> User:
        """Resolve a user from an access token.

        Args:
            db: SQLAlchemy session.
            token: Access token string from the Authorization header.

        Returns:
            The `User` represented by the token.

        Raises:
            HTTPException: If token is invalid or user not found.
        """

        try:
            payload = decode_token(token)
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

        user = db.execute(select(User).where(User.id == int(user_id))).scalar_one_or_none()
        if user is None or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
        return user

