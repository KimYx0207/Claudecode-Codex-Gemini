"""Utility functions for JWT handling and password hashing.

This module provides helpers to create/verify JWTs and to hash/verify
passwords using bcrypt via Passlib.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Tuple
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import Settings, get_settings


_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a plaintext password using bcrypt.

    Args:
        password: Plaintext password.

    Returns:
        The hashed password string.
    """

    return _pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its bcrypt hash.

    Args:
        plain_password: User supplied plaintext password.
        hashed_password: Stored bcrypt password hash.

    Returns:
        True if the password matches; otherwise, False.
    """

    return _pwd_context.verify(plain_password, hashed_password)


def _now_utc() -> datetime:
    """Get current UTC datetime with timezone info.

    Returns:
        Current UTC time with timezone awareness.
    """

    return datetime.now(timezone.utc)


def create_access_token(user_id: int, settings: Settings | None = None) -> str:
    """Create a signed JWT access token.

    Args:
        user_id: Subject user ID for the token.
        settings: Optional settings override; uses global settings if omitted.

    Returns:
        Encoded JWT access token string.
    """

    s = settings or get_settings()
    now = _now_utc()
    expire = now + timedelta(minutes=s.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode: Dict[str, Any] = {
        "sub": str(user_id),
        "type": "access",
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(to_encode, s.SECRET_KEY, algorithm=s.ALGORITHM)


def create_refresh_token(
    user_id: int, settings: Settings | None = None
) -> Tuple[str, str, datetime]:
    """Create a signed JWT refresh token along with JTI and expiration.

    Args:
        user_id: Subject user ID for the token.
        settings: Optional settings override; uses global settings if omitted.

    Returns:
        A tuple of (refresh_token, jti, expires_at_utc).
    """

    s = settings or get_settings()
    now = _now_utc()
    expire = now + timedelta(days=s.REFRESH_TOKEN_EXPIRE_DAYS)
    jti = uuid4().hex
    to_encode: Dict[str, Any] = {
        "sub": str(user_id),
        "type": "refresh",
        "jti": jti,
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    token = jwt.encode(to_encode, s.SECRET_KEY, algorithm=s.ALGORITHM)
    return token, jti, expire


def decode_token(token: str, settings: Settings | None = None) -> Dict[str, Any]:
    """Decode and verify a JWT.

    Args:
        token: Encoded JWT string.
        settings: Optional settings override; uses global settings if omitted.

    Returns:
        Decoded JWT claims dictionary.

    Raises:
        JWTError: If the token is invalid or expired.
    """

    s = settings or get_settings()
    return jwt.decode(token, s.SECRET_KEY, algorithms=[s.ALGORITHM])


def hash_token(token: str) -> str:
    """Compute a SHA-256 hash of a token for safe storage.

    Args:
        token: Raw token string.

    Returns:
        Hex-encoded SHA-256 hash string.
    """

    return hashlib.sha256(token.encode("utf-8")).hexdigest()

