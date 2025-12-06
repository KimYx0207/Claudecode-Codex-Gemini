"""Pytest configuration and shared fixtures.

Provides common test fixtures for database sessions, test users, and async support.
"""

from __future__ import annotations

import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# Set test environment before importing app modules
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from src.core.database import Base


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Select async backend for pytest-asyncio."""
    return "asyncio"


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test.

    Uses an in-memory SQLite database that is created fresh for each test.

    Yields:
        AsyncSession: Database session for testing.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
        class_=AsyncSession,
    )

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.fixture
def test_user_data() -> dict[str, str]:
    """Provide sample user registration data.

    Returns:
        dict: User registration payload.
    """
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "SecurePassword123!",
    }
