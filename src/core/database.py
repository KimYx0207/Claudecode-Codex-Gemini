"""Database configuration and session management using SQLAlchemy async.

This module sets up an async SQLAlchemy engine and session factory, and provides
FastAPI-compatible dependencies for obtaining a database session.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


class Base(DeclarativeBase):
    """Declarative base for ORM models."""


def _get_database_url() -> str:
    """Resolve database URL from environment.

    Defaults to a local SQLite database using aiosqlite driver.

    Returns:
        str: The database URL.
    """

    return os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")


DATABASE_URL: str = _get_database_url()

# Create async engine
engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
    class_=AsyncSession,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session.

    Yields:
        AsyncSession: An active async SQLAlchemy session.
    """

    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
