from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import (
    UserCreate,
    UserResponse,
    Token,
    PasswordResetRequest,
    PasswordResetConfirm,
    VerifyOtpRequest,
    GoogleLoginRequest,
    LoginRequest,
)
from app.auth.service import (
    create_user,
    authenticate_user,
    create_password_reset_otp,
    reset_password,
    verify_otp,
    activate_user,
    process_password_reset_request,
)
from app.auth.utils import create_access_token
from app.core.database import get_db_session

router = APIRouter(tags=["Auth"])


@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_create: UserCreate, db: Annotated[AsyncSession, Depends(get_db_session)]
):
    """Register a new user."""
    user, otp = await create_user(db, user_create)
    # Return OTP for demo purposes so user can verify
    return {
        "id": user.id,
        "email": user.email,
        "message": "Registration successful. Please verify your email with the OTP.",
        "otp": otp,
    }


@router.post("/auth/verify-otp")
async def verify_otp_endpoint(
    request: VerifyOtpRequest, db: Annotated[AsyncSession, Depends(get_db_session)]
):
    """Verify OTP and activate account."""
    await verify_otp(request.email, request.otp, purpose="verify")
    await activate_user(db, request.email)
    return {"message": "Account verified successfully."}


@router.post("/auth/login", response_model=Token)
async def login(
    login_request: LoginRequest, db: Annotated[AsyncSession, Depends(get_db_session)]
):
    """Login with email and password (JSON)."""
    user = await authenticate_user(db, login_request.email, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if hasattr(user, "is_verified") and not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not verified. Please verify your email.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/auth/forgot-password")
async def forgot_password(
    request: PasswordResetRequest,
):
    """Request a password reset OTP."""
    await process_password_reset_request(request.email)

    return {
        "message": "If an account exists with this email, a password reset code has been sent.",
    }


@router.post("/auth/verify-password-otp")
async def verify_password_otp(request: VerifyOtpRequest):
    """Verify Password Reset OTP."""
    await verify_otp(
        request.email, request.otp, purpose="reset", delete_on_success=False
    )
    return {"message": "OTP verified. Proceed to reset password."}


@router.post("/auth/reset-password")
async def confirm_reset_password(
    request: PasswordResetConfirm, db: Annotated[AsyncSession, Depends(get_db_session)]
):
    """Reset password using OTP."""
    await reset_password(db, request.email, request.otp, request.new_password)
    return {"message": "Password successfully reset."}


@router.post("/auth/google/login")
async def google_login(
    request: GoogleLoginRequest, db: Annotated[AsyncSession, Depends(get_db_session)]
):
    """Google Login (Placeholder)."""
    # Logic to verify Google token and create/get user would go here
    return {"message": "Google login not implemented yet"}
