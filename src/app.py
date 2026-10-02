"""Minimal FastAPI application wiring the auth router.

Run with:
    uvicorn src.app:app --reload
"""

from __future__ import annotations

from fastapi import FastAPI

from src.auth.router import router as auth_router
from src.core.database import Base, engine

app = FastAPI(title="Auth Service")
app.include_router(auth_router)


@app.on_event("startup")
async def on_startup() -> None:
    """Create database tables on startup (for demo/dev usage)."""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def root() -> dict[str, str]:
    """Health check endpoint."""

    return {"status": "ok"}
