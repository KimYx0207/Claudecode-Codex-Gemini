"""FastAPI dependencies for authenticated operations."""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,  # noqa: TC002 - FastAPI resolves dependency annotations
)

from src.auth.models import User
from src.auth.utils import decode_token
from src.core.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    """Resolve the current authenticated user from a bearer token.

    Args:
        token (str): Bearer token provided by the client.
        db (AsyncSession): Database session dependency.

    Returns:
        User: The authenticated user entity.

    Raises:
        HTTPException: If token is invalid, not an access token, or user not found.
    """

    payload = decode_token(token)
    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing subject"
        )

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive"
        )
    return user
