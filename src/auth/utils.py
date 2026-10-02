"""Authentication utility functions.

Includes password hashing/verification and JWT creation/decoding helpers.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash.

    Args:
        plain_password (str): The plaintext password to verify.
        hashed_password (str): The bcrypt-hashed password for comparison.

    Returns:
        bool: True if the password matches, otherwise False.
    """

    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a plaintext password using bcrypt.

    Args:
        password (str): The plaintext password.

    Returns:
        str: The resulting bcrypt hash.
    """

    return pwd_context.hash(password)


def _expire_time(delta: timedelta | None) -> datetime:
    """Compute an expiration datetime in UTC.

    Args:
        delta (Optional[timedelta]): Optional time delta to add to current UTC time.

    Returns:
        datetime: The resulting expiration time.
    """

    now = datetime.now(UTC)
    return now + (delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT access token.

    Args:
        data (Dict[str, Any]): Base claims to include in the token payload.
        expires_delta (Optional[timedelta]): Optional lifetime; defaults to configured minutes.

    Returns:
        str: Encoded JWT access token string.
    """

    to_encode = data.copy()
    expire = _expire_time(expires_delta)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT refresh token.

    Args:
        data (Dict[str, Any]): Base claims to include in the token payload.
        expires_delta (Optional[timedelta]): Optional lifetime; defaults to configured days.

    Returns:
        str: Encoded JWT refresh token string.
    """

    to_encode = data.copy()
    default_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    expire = datetime.now(UTC) + (expires_delta or default_delta)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT token.

    Args:
        token (str): Encoded JWT string.

    Returns:
        Dict[str, Any]: Decoded payload.

    Raises:
        HTTPException: If token is invalid or expired.
    """

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        ) from None
