"""Pydantic v2 schemas for authentication APIs."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Request body for user registration.

    Attributes:
        email (EmailStr): User email address.
        username (str): Desired username.
        password (str): Plain password to be hashed.
    """

    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)


class UserLoginRequest(BaseModel):
    """Request body for user login.

    Attributes:
        email (EmailStr): User email address.
        password (str): Plain password.
    """

    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class TokenResponse(BaseModel):
    """Response body containing issued tokens.

    Attributes:
        access_token (str): The short-lived access token (JWT).
        refresh_token (str): The long-lived refresh token (JWT).
        token_type (Literal["bearer"]): Token type marker.
        expires_in (int): Access token expiry in seconds.
    """

    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Request body to refresh an access token.

    Attributes:
        refresh_token (str): The refresh token.
    """

    refresh_token: str


class UserResponse(BaseModel):
    """Response body for user metadata.

    Attributes:
        id (str): User identifier.
        email (EmailStr): Email address.
        username (str): Username.
        is_active (bool): Active status.
        created_at (datetime): Creation timestamp.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    username: str
    is_active: bool
    created_at: datetime
