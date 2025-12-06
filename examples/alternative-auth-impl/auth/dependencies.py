"""Authentication-related FastAPI dependencies.

Provides helpers to obtain a database session and the current user from
the Authorization header using a Bearer access token.
"""

from __future__ import annotations

from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.models import SessionLocal, User
from app.auth.service import AuthService


security = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session for request scope.

    Yields:
        Session: Database session for use within request handlers.
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Extract and validate the current user from Bearer token.

    Args:
        credentials: Parsed authorization header credentials.
        db: SQLAlchemy session (injected).

    Returns:
        The authenticated `User` instance.

    Raises:
        HTTPException: If credentials are missing or invalid.
    """

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = credentials.credentials

    service = AuthService()
    return service.get_user_from_access_token(db, token)

