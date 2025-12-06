"""Tests for authentication utility functions.

Tests password hashing, verification, and JWT token operations.
"""

from __future__ import annotations

from datetime import timedelta

import pytest

from src.auth.utils import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)


class TestPasswordHashing:
    """Tests for password hashing and verification."""

    def test_hash_password_returns_hash(self) -> None:
        """Password hashing should return a bcrypt hash string."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password
        assert hashed.startswith("$2b$")  # bcrypt identifier

    def test_verify_password_correct(self) -> None:
        """Correct password should verify successfully."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)

        result = verify_password(password, hashed)

        assert result is True

    def test_verify_password_incorrect(self) -> None:
        """Incorrect password should fail verification."""
        password = "TestPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = get_password_hash(password)

        result = verify_password(wrong_password, hashed)

        assert result is False

    def test_different_passwords_produce_different_hashes(self) -> None:
        """Different passwords should produce different hashes."""
        hash1 = get_password_hash("Password1")
        hash2 = get_password_hash("Password2")

        assert hash1 != hash2

    def test_same_password_produces_different_hashes(self) -> None:
        """Same password should produce different hashes (due to salt)."""
        password = "SamePassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Both should verify
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)
        # But hashes should differ (different salts)
        assert hash1 != hash2


class TestJWTTokens:
    """Tests for JWT token creation and decoding."""

    def test_create_access_token(self) -> None:
        """Access token should be created with correct claims."""
        data = {"sub": "user123"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self) -> None:
        """Refresh token should be created with correct claims."""
        data = {"sub": "user123"}
        token = create_refresh_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_valid_access_token(self) -> None:
        """Valid access token should decode successfully."""
        user_id = "user-uuid-123"
        data = {"sub": user_id}
        token = create_access_token(data)

        payload = decode_token(token)

        assert payload["sub"] == user_id
        assert payload["type"] == "access"
        assert "exp" in payload

    def test_decode_valid_refresh_token(self) -> None:
        """Valid refresh token should decode successfully."""
        user_id = "user-uuid-456"
        data = {"sub": user_id}
        token = create_refresh_token(data)

        payload = decode_token(token)

        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"
        assert "exp" in payload

    def test_access_token_with_custom_expiry(self) -> None:
        """Access token should respect custom expiry delta."""
        data = {"sub": "user123"}
        delta = timedelta(hours=2)
        token = create_access_token(data, expires_delta=delta)

        payload = decode_token(token)

        assert payload["sub"] == "user123"

    def test_decode_invalid_token_raises_exception(self) -> None:
        """Invalid token should raise HTTPException."""
        from fastapi import HTTPException

        invalid_token = "invalid.token.string"

        with pytest.raises(HTTPException) as exc_info:
            decode_token(invalid_token)

        assert exc_info.value.status_code == 401
