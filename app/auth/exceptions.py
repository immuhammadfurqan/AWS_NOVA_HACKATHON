"""
Authentication and Authorization Exceptions
"""

from typing import Optional

from app.core.exceptions import AARLPException


class AuthenticationError(AARLPException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__(message=message, error_code="AUTH_ERROR")


class AuthorizationError(AARLPException):
    """Raised when user lacks required permissions."""

    def __init__(
        self,
        message: str = "Permission denied",
        required_permission: Optional[str] = None,
    ) -> None:
        super().__init__(
            message=message,
            error_code="FORBIDDEN",
            details=(
                {"required_permission": required_permission}
                if required_permission
                else {}
            ),
        )


class InvalidCredentialsError(AuthenticationError):
    """Raised when login credentials are invalid."""

    def __init__(self) -> None:
        super().__init__(message="Invalid credentials")


class InvalidOTPError(AARLPException):
    """Raised when OTP is invalid or expired."""

    def __init__(self) -> None:
        super().__init__(
            message="Invalid or expired verification code",
            error_code="INVALID_OTP",
        )


class OTPExpiredError(AARLPException):
    """Raised when no OTP is found (expired)."""

    def __init__(self) -> None:
        super().__init__(
            message="No OTP found for this email. It may have expired.",
            error_code="OTP_EXPIRED",
        )


class InactiveUserError(AuthenticationError):
    """Raised when user account is inactive."""

    def __init__(self) -> None:
        super().__init__(message="Account is inactive")


class UnverifiedUserError(AuthenticationError):
    """Raised when user account is not verified."""

    def __init__(self) -> None:
        super().__init__(message="Account not verified. Please check your email.")


class EmailExistsError(AARLPException):
    """Raised when email already exists."""

    def __init__(self) -> None:
        super().__init__(
            message="A user with this email already exists.",
            error_code="EMAIL_EXISTS",
        )


class UserNotFoundError(AARLPException):
    """Raised when user is not found."""

    def __init__(self) -> None:
        super().__init__(
            message="User not found.",
            error_code="USER_NOT_FOUND",
        )
