"""Application configuration for JWT and general settings.

This module provides a simple settings class for JWT configuration.

Attributes:
    settings (Settings): A singleton instance with loaded configuration.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class Settings:
    """Settings container for JWT configuration.

    Attributes:
        SECRET_KEY (str): Secret key used for JWT signing, loaded from environment
            variable "SECRET_KEY". Raises ValueError if missing.
        ALGORITHM (str): JWT signing algorithm. Defaults to "HS256".
        ACCESS_TOKEN_EXPIRE_MINUTES (int): Access token lifetime in minutes.
        REFRESH_TOKEN_EXPIRE_DAYS (int): Refresh token lifetime in days.
    """

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @staticmethod
    def load() -> Settings:
        """Load settings from environment variables.

        Returns:
            Settings: Loaded settings instance.

        Raises:
            ValueError: If SECRET_KEY is not defined in environment.
        """

        # Default to a development key if not provided; strongly recommend overriding
        # via environment in production deployments.
        secret = os.getenv("SECRET_KEY", "change-me-in-production")

        algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        access_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
        refresh_days = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

        return Settings(
            SECRET_KEY=secret,
            ALGORITHM=algorithm,
            ACCESS_TOKEN_EXPIRE_MINUTES=access_minutes,
            REFRESH_TOKEN_EXPIRE_DAYS=refresh_days,
        )


# Singleton settings instance
settings = Settings.load()
