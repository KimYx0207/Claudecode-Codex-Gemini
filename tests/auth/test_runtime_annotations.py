"""Protect runtime annotation consumers while keeping type-only imports narrow."""

from __future__ import annotations

from datetime import datetime
from typing import get_type_hints

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from src.app import app
from src.auth.dependencies import get_current_user
from src.auth.models import RefreshToken, User
from src.auth.schemas import UserResponse


def test_auth_openapi_schema_loads() -> None:
    """FastAPI must resolve route and request annotations during schema generation."""
    schema = app.openapi()

    assert {"/register", "/login", "/refresh", "/me"} <= schema["paths"].keys()
    schemas = schema["components"]["schemas"]
    assert schemas["UserLoginRequest"]["required"] == ["email", "password"]
    assert schemas["UserResponse"]["properties"]["created_at"]["format"] == "date-time"


def test_dependency_annotations_resolve_at_runtime() -> None:
    """Undecorated FastAPI dependencies also need their annotation imports."""
    hints = get_type_hints(get_current_user)

    assert hints["db"] is AsyncSession
    assert hints["return"] is User


def test_model_datetime_annotations_resolve_at_runtime() -> None:
    """SQLAlchemy and Pydantic must retain datetime imports outside TYPE_CHECKING."""
    assert User.__table__.c.created_at.type.python_type is datetime
    assert RefreshToken.__table__.c.expires_at.type.python_type is datetime
    assert UserResponse.model_fields["created_at"].annotation is datetime


async def test_health_and_unauthenticated_routes() -> None:
    """Smoke-test the in-process ASGI app without external services or real accounts."""
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        health = await client.get("/")
        protected = await client.get("/me")

    assert health.status_code == 200
    assert health.json() == {"status": "ok"}
    assert protected.status_code == 401
