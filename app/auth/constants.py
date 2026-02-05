"""
Authentication constants.

Centralized configuration for auth module.
"""


class OTPSettings:
    """OTP configuration."""

    LENGTH = 6
    EXPIRY_MINUTES = 15
    ALLOWED_PURPOSES = {"verify", "reset"}
    KEY_PREFIX = "otp"


class PasswordSettings:
    """Password requirements."""

    MIN_LENGTH = 8
    MAX_LENGTH = 128


class Messages:
    """Response messages."""

    REGISTRATION_SUCCESS = (
        "Registration successful. Please verify your email with the OTP."
    )
    ACCOUNT_VERIFIED = "Account verified successfully."
    PASSWORD_RESET = "Password successfully reset."
    INVALID_CREDENTIALS = "Invalid credentials"
    OTP_SENT = (
        "If an account exists with this email, a password reset code has been sent."
    )
