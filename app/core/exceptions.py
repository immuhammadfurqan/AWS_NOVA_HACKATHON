"""
AARLP Custom Exceptions

Defines application-specific exceptions for better error handling
and debugging. All exceptions inherit from a base AARLPException.
"""

from typing import Any, Optional


class AARLPException(Exception):
    """Base exception for all AARLP errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.error_code = error_code or "AARLP_ERROR"
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }


# ============================================================================
# Configuration Exceptions
# ============================================================================


class ConfigurationError(AARLPException):
    """Raised when configuration is invalid or missing."""

    def __init__(self, message: str, config_key: Optional[str] = None) -> None:
        super().__init__(
            message=message,
            error_code="CONFIG_ERROR",
            details={"config_key": config_key} if config_key else {},
        )


# ============================================================================
# Database Exceptions
# ============================================================================


class DatabaseError(AARLPException):
    """Base exception for database-related errors."""

    def __init__(self, message: str, operation: Optional[str] = None) -> None:
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details={"operation": operation} if operation else {},
        )


class RecordNotFoundError(DatabaseError):
    """Raised when a requested record is not found."""

    def __init__(self, resource: str, resource_id: str) -> None:
        super().__init__(
            message=f"{resource} with ID {resource_id} not found",
            operation="SELECT",
        )
        self.error_code = "NOT_FOUND"
        self.details = {"resource": resource, "resource_id": resource_id}


class DuplicateRecordError(DatabaseError):
    """Raised when attempting to create a duplicate record."""

    def __init__(self, resource: str, identifier: str) -> None:
        super().__init__(
            message=f"{resource} with identifier {identifier} already exists",
            operation="INSERT",
        )
        self.error_code = "DUPLICATE_RECORD"


# ============================================================================
# External Service Exceptions
# ============================================================================


class ExternalServiceError(AARLPException):
    """Base exception for external service failures."""

    def __init__(
        self,
        service: str,
        message: str,
        status_code: Optional[int] = None,
    ) -> None:
        super().__init__(
            message=f"{service}: {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service, "status_code": status_code},
        )


# ============================================================================
# Security Exceptions
# ============================================================================


class ForbiddenError(AARLPException):
    """Raised when a user attempts to access a resource they do not own."""

    def __init__(self, resource: str, user_id: str) -> None:
        super().__init__(
            message="You do not have permission to access this resource",
            error_code="FORBIDDEN",
            details={"resource": resource, "user_id": str(user_id)},
        )


# ============================================================================
# Validation Exceptions
# ============================================================================


class ValidationError(AARLPException):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: Optional[str] = None) -> None:
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details={"field": field} if field else {},
        )
