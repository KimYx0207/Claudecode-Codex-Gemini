"""Application settings and JWT configuration.

This module centralizes configuration for JWT and database settings.
Values can be overridden via environment variables.

Google-style docstrings are used across the codebase.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    """Settings container for application configuration.

    Attributes:
        SECRET_KEY: Secret used to sign JWTs.
        ALGORITHM: JWT signing algorithm.
        ACCESS_TOKEN_EXPIRE_MINUTES: Access token lifetime in minutes.
        REFRESH_TOKEN_EXPIRE_DAYS: Refresh token lifetime in days.
        DATABASE_URL: SQLAlchemy database URL.
    """

    SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "change-me-in-prod"))
    ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get a cached instance of application settings.

    Returns:
        Settings: Singleton-like cached settings instance.
    """

    return Settings()

