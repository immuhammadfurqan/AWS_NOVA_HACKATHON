"""
Core Exceptions Tests

Unit tests for custom exception classes.
"""

import pytest

from app.core.exceptions import (
    AARLPException,
    RecordNotFoundError,
    ValidationError,
    ForbiddenError,
    ExternalServiceError,
    ConfigurationError,
    DuplicateRecordError,
)


class TestAARLPException:
    """Tests for base AARLPException."""

    def test_exception_message(self):
        """Exception should store message."""
        exc = AARLPException("Test error")

        assert exc.message == "Test error"
        assert str(exc) == "Test error"

    def test_exception_error_code(self):
        """Exception should have error code."""
        exc = AARLPException("Test error", error_code="TEST_ERROR")

        assert exc.error_code == "TEST_ERROR"

    def test_exception_details(self):
        """Exception should store details."""
        exc = AARLPException(
            "Test error", details={"field": "email", "value": "invalid"}
        )

        assert exc.details["field"] == "email"

    def test_to_dict(self):
        """Exception should convert to dict for API response."""
        exc = AARLPException(
            "Test error", error_code="TEST_ERROR", details={"key": "value"}
        )

        result = exc.to_dict()

        assert result["error_code"] == "TEST_ERROR"
        assert result["message"] == "Test error"
        assert result["details"]["key"] == "value"


class TestRecordNotFoundError:
    """Tests for RecordNotFoundError."""

    def test_not_found_message(self):
        """Not found should have descriptive message."""
        exc = RecordNotFoundError("Job", "123-456")

        assert "Job" in exc.message
        assert "123-456" in exc.message
        assert exc.error_code == "NOT_FOUND"

    def test_not_found_details(self):
        """Not found should include resource info in details."""
        exc = RecordNotFoundError("Job", "123-456")

        assert exc.details["resource"] == "Job"
        assert exc.details["resource_id"] == "123-456"


class TestValidationError:
    """Tests for ValidationError."""

    def test_validation_error_message(self):
        """Validation error should have message."""
        exc = ValidationError("Email is required", field="email")

        assert exc.message == "Email is required"
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.details["field"] == "email"


class TestForbiddenError:
    """Tests for ForbiddenError."""

    def test_forbidden_message(self):
        """Forbidden should have generic message (security)."""
        exc = ForbiddenError("Job", "user-123")

        assert "permission" in exc.message.lower()
        assert exc.error_code == "FORBIDDEN"


class TestExternalServiceError:
    """Tests for ExternalServiceError."""

    def test_external_service_error(self):
        """External service error should include service name."""
        exc = ExternalServiceError(
            service="OpenAI", message="Rate limit exceeded", status_code=429
        )

        assert "OpenAI" in exc.message
        assert exc.details["status_code"] == 429


class TestDuplicateRecordError:
    """Tests for DuplicateRecordError."""

    def test_duplicate_error(self):
        """Duplicate error should have correct code."""
        exc = DuplicateRecordError("User", "test@example.com")

        assert "already exists" in exc.message
        assert exc.error_code == "DUPLICATE_RECORD"


class TestConfigurationError:
    """Tests for ConfigurationError."""

    def test_config_error(self):
        """Config error should include config key."""
        exc = ConfigurationError("Missing API key", config_key="OPENAI_API_KEY")

        assert exc.error_code == "CONFIG_ERROR"
        assert exc.details["config_key"] == "OPENAI_API_KEY"
