from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt_dependencies import get_current_user
from app.auth.models import User
from app.auth.schemas import UserResponse
from app.auth.utils import verify_password, get_password_hash
from app.core.database import get_db_session
from app.users.schemas import UserUpdate, ChangePasswordRequest

router = APIRouter(tags=["Users"])


@router.get("/users/me", response_model=UserResponse)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Get current authenticated user info."""
    return current_user


@router.patch("/users/me", response_model=UserResponse)
async def update_user_me(
    user_update: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)]
):
    """Update current user info."""
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    if user_update.email is not None:
        # Check if email is taken? For now just update
        # In real app, check duplication
        current_user.email = user_update.email
    
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.patch("/users/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)]
):
    """Change current user password."""
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    current_user.hashed_password = get_password_hash(request.new_password)
    
    await db.commit()
    return {"message": "Password updated successfully"}
