"""
JWT Dependencies

Token validation and current user retrieval.
"""

from typing import Annotated

from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.schemas import TokenData
from app.auth.service import get_user_by_email
from app.auth.exceptions import InvalidCredentialsError
from app.core.config import get_settings
from app.core.database import get_db_session

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> User:
    """Validate token and get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",  # Generic message to prevent enumeration
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        sub: str | None = payload.get("sub")
        if sub is None:
            raise credentials_exception

        token_data = TokenData(sub=sub)
    except JWTError:
        raise credentials_exception

    user = await get_user_by_email(db, email=token_data.sub)
    if user is None:
        raise credentials_exception

    # Use same generic message to prevent user enumeration
    if not user.is_active or not user.is_verified:
        raise credentials_exception

    return user
