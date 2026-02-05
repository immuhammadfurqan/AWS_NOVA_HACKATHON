"""
Auth Service

Authentication and user management business logic.
Uses Redis for OTP storage to support horizontal scaling.
"""

from typing import Optional
import hashlib
import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.schemas import UserCreate
from app.auth.utils import get_password_hash, verify_password
from app.auth.constants import OTPSettings
from app.auth.exceptions import (
    InvalidOTPError,
    OTPExpiredError,
    EmailExistsError,
    UserNotFoundError,
)
from app.core.email import send_otp_email, send_password_reset_email
from app.core.exceptions import AARLPException
from app.core.logging import get_logger

logger = get_logger(__name__)


async def _get_redis():
    """Get Redis client for OTP storage."""
    from app.core.locking import get_redis

    return await get_redis()


def _hash_otp(otp: str) -> str:
    return hashlib.sha256(otp.encode("utf-8")).hexdigest()


def _normalize_redis_value(value: object | None) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return str(value)


def _otp_key(email: str, purpose: str) -> str:
    return f"{OTPSettings.KEY_PREFIX}:{purpose}:{email}"


def _generate_otp() -> str:
    return "".join(str(secrets.randbelow(10)) for _ in range(OTPSettings.LENGTH))


async def create_otp(email: str, purpose: str) -> str:
    """
    Generate a 6-digit password reset OTP and store in Redis.

    Args:
        email: User's email address

    Returns:
        The generated OTP string
    """
    otp = _generate_otp()

    try:
        redis = await _get_redis()
        key = _otp_key(email, purpose)
        # Store OTP with TTL (auto-expires)
        await redis.setex(key, OTPSettings.EXPIRY_MINUTES * 60, _hash_otp(otp))
        logger.debug(f"OTP created for {email}")
    except Exception as e:
        logger.error(f"Failed to store OTP in Redis: {e}")
        raise AARLPException(
            error_code="OTP_STORAGE_FAILED",
            message="Unable to create OTP. Please try again.",
        )

    return otp


async def create_password_reset_otp(email: str) -> str:
    """Generate and store a password reset OTP."""
    return await create_otp(email, purpose="reset")


async def create_email_verification_otp(email: str) -> str:
    """Generate and store an email verification OTP."""
    return await create_otp(email, purpose="verify")


async def process_password_reset_request(email: str) -> None:
    """
    Handle the flow for requesting a password reset.
    Generates OTP and sends email.

    Args:
        email: The user's email address
    """
    otp = await create_password_reset_otp(email)

    try:
        await send_password_reset_email(email, otp)
    except Exception as e:
        logger.error(f"Failed to send password reset email to {email}: {e}")
        raise AARLPException(
            error_code="EMAIL_SENDING_FAILED",
            message="Failed to send password reset email.",
        )


async def _get_stored_otp_hash(email: str, purpose: str) -> Optional[str]:
    """Retrieve hashed OTP from Redis."""
    try:
        redis = await _get_redis()
        key = _otp_key(email, purpose)
        return _normalize_redis_value(await redis.get(key))
    except Exception as e:
        logger.error(f"Failed to retrieve OTP from Redis: {e}")
        return None


async def _delete_otp(email: str, purpose: str) -> None:
    """Delete OTP from Redis after use."""
    try:
        redis = await _get_redis()
        key = _otp_key(email, purpose)
        await redis.delete(key)
    except Exception as e:
        logger.warning(f"Failed to delete OTP from Redis: {e}")


async def verify_otp(
    email: str, otp: str, purpose: str, delete_on_success: bool = True
) -> bool:
    """
    Verify an OTP.

    Args:
        email: User's email address
        otp: The OTP to verify

    Returns:
        True if OTP is valid

    Raises:
        AARLPException: If OTP is invalid or expired
    """
    stored_otp_hash = await _get_stored_otp_hash(email, purpose)

    if not stored_otp_hash:
        raise OTPExpiredError()

    if stored_otp_hash != _hash_otp(otp):
        raise InvalidOTPError()

    if delete_on_success:
        await _delete_otp(email, purpose)

    return True


async def activate_user(db: AsyncSession, email: str) -> None:
    """Mark user as verified and clean up OTP."""
    user = await get_user_by_email(db, email)
    if not user:
        raise UserNotFoundError()
    user.is_verified = True
    await db.commit()
    await db.refresh(user)
    logger.info(f"User {email} activated")


async def reset_password(
    db: AsyncSession, email: str, otp: str, new_password: str
) -> User:
    """
    Reset password using email and OTP.

    Args:
        db: Database session
        email: User's email
        otp: The OTP to verify
        new_password: The new password to set

    Returns:
        The updated User object
    """
    # Verify OTP first (single-use)
    await verify_otp(email, otp, purpose="reset")

    user = await get_user_by_email(db, email)

    if not user:
        raise UserNotFoundError()

    user.hashed_password = get_password_hash(new_password)

    await db.commit()
    await db.refresh(user)

    logger.info(f"Password reset for {email}")
    return user


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get a user by email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_create: UserCreate) -> tuple[User, str]:
    """
    Create a new user and generate verification OTP.

    Args:
        db: Database session
        user_create: User creation data

    Returns:
        Tuple of (User, OTP string)
    """
    existing_user = await get_user_by_email(db, user_create.email)
    if existing_user:
        raise EmailExistsError()

    hashed_password = get_password_hash(user_create.password)

    db_user = User(
        email=user_create.email,
        hashed_password=hashed_password,
        full_name=user_create.full_name,
        is_active=True,
        is_verified=False,  # Enforce verification
        is_superuser=False,
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    # Generate OTP
    otp = await create_email_verification_otp(db_user.email)

    # Send OTP via Email
    try:
        await send_otp_email(db_user.email, otp)
    except Exception as e:
        logger.error(f"Failed to send verification email to {db_user.email}: {e}")
        # Don't fail registration, but log the error

    logger.info(f"User created: {db_user.email}")
    return db_user, otp


async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> Optional[User]:
    """
    Authenticate a user.

    Args:
        db: Database session
        email: User's email
        password: Password to verify

    Returns:
        User if authentication successful, None otherwise
    """
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active or not user.is_verified:
        return None

    return user
