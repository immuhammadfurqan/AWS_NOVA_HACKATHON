"""
Auth Service Tests

Unit tests for authentication service functions.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from app.auth.service import (
    create_access_token,
    verify_password,
    get_password_hash,
)
from app.auth.schemas import UserCreate
from app.core.config import get_settings


class TestPasswordHashing:
    """Tests for password hashing functions."""

    def test_password_hash_is_different_from_plain(self):
        """Hashed password should differ from plain text."""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 0

    def test_password_verification_success(self):
        """Correct password should verify successfully."""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_password_verification_failure(self):
        """Incorrect password should fail verification."""
        password = "SecurePassword123!"
        wrong_password = "WrongPassword456!"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_same_password_produces_different_hashes(self):
        """Same password should produce different hashes (salting)."""
        password = "SecurePassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Hashes should be different due to salt
        assert hash1 != hash2
        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestAccessToken:
    """Tests for JWT token creation."""

    def test_create_access_token_returns_string(self):
        """Token creation should return a non-empty string."""
        token = create_access_token(data={"sub": "test@example.com"})

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_expiry(self):
        """Token with custom expiry should be created."""
        expires = timedelta(minutes=15)
        token = create_access_token(
            data={"sub": "test@example.com"}, expires_delta=expires
        )

        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_contains_subject(self):
        """Token should contain the subject when decoded."""
        from jose import jwt

        settings = get_settings()

        email = "test@example.com"
        token = create_access_token(data={"sub": email})

        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )

        assert payload.get("sub") == email

    def test_token_has_expiration(self):
        """Token should have an expiration time."""
        from jose import jwt

        settings = get_settings()

        token = create_access_token(data={"sub": "test@example.com"})
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )

        assert "exp" in payload


class TestUserValidation:
    """Tests for user input validation."""

    def test_valid_user_create(self):
        """Valid user data should pass validation."""
        user = UserCreate(
            email="test@example.com",
            password="SecurePassword123!",
            full_name="Test User",
        )

        assert user.email == "test@example.com"
        assert user.full_name == "Test User"

    def test_invalid_email_rejected(self):
        """Invalid email format should be rejected."""
        with pytest.raises(ValueError):
            UserCreate(
                email="invalid-email",
                password="SecurePassword123!",
                full_name="Test User",
            )

    def test_short_password_rejected(self):
        """Short passwords should be rejected."""
        with pytest.raises(ValueError):
            UserCreate(
                email="test@example.com", password="short", full_name="Test User"
            )
