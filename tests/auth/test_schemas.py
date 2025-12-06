"""Tests for Pydantic validation schemas.

Tests input validation for user registration and authentication.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.auth.schemas import UserCreate, UserLogin


class TestUserCreateSchema:
    """Tests for UserCreate schema validation."""

    def test_valid_user_create(self) -> None:
        """Valid user data should pass validation."""
        user = UserCreate(
            email="test@example.com",
            username="testuser",
            password="SecurePassword123!",
        )

        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.password == "SecurePassword123!"

    def test_invalid_email_raises_error(self) -> None:
        """Invalid email format should raise ValidationError."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="not-an-email",
                username="testuser",
                password="SecurePassword123!",
            )

    def test_empty_username_raises_error(self) -> None:
        """Empty username should raise ValidationError."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                username="",
                password="SecurePassword123!",
            )

    def test_short_password_raises_error(self) -> None:
        """Password shorter than minimum should raise ValidationError."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                username="testuser",
                password="short",
            )


class TestUserLoginSchema:
    """Tests for UserLogin schema validation."""

    def test_valid_login_with_email(self) -> None:
        """Valid login with email should pass validation."""
        login = UserLogin(
            email="test@example.com",
            password="SecurePassword123!",
        )

        assert login.email == "test@example.com"
        assert login.password == "SecurePassword123!"

    def test_valid_login_with_username(self) -> None:
        """Valid login with username should pass validation."""
        login = UserLogin(
            username="testuser",
            password="SecurePassword123!",
        )

        assert login.username == "testuser"
        assert login.password == "SecurePassword123!"

    def test_missing_password_raises_error(self) -> None:
        """Missing password should raise ValidationError."""
        with pytest.raises(ValidationError):
            UserLogin(
                email="test@example.com",
                password="",
            )
