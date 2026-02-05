"""
Auth Schemas - Refactored

Clean Code improvements:
- Password strength validation
- Response models for API endpoints
- Reusable field types
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, constr, field_validator

from app.auth.constants import PasswordSettings

OtpCode = constr(min_length=6, max_length=6, pattern=r"^\d+$")


# ============================================================================
# BASE MODELS
# ============================================================================


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


# ============================================================================
# REQUEST MODELS
# ============================================================================


class UserCreate(UserBase):
    """User registration request with password validation."""

    password: str = Field(
        ...,
        min_length=PasswordSettings.MIN_LENGTH,
        max_length=PasswordSettings.MAX_LENGTH,
        description="Password (8-128 characters, must include uppercase, lowercase, and digit)",
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Ensure password meets security requirements."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation with validated new password."""

    email: EmailStr
    otp: OtpCode
    new_password: str = Field(
        ...,
        min_length=PasswordSettings.MIN_LENGTH,
        max_length=PasswordSettings.MAX_LENGTH,
        description="New password (8-128 characters)",
    )

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Ensure password meets security requirements."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: OtpCode


class GoogleLoginRequest(BaseModel):
    token: str


# ============================================================================
# RESPONSE MODELS
# ============================================================================


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: Optional[str] = None


class UserResponse(UserBase):
    """User data response."""

    id: UUID
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True


class RegistrationResponse(BaseModel):
    """Response after user registration."""

    id: UUID
    email: EmailStr
    message: str
    otp: Optional[str] = None  # Only for development
