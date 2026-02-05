"""
Careers Dependencies

Dependency injection for careers module.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.careers.repository import CareersRepository
from app.careers.service import CareersService


async def get_careers_repository(
    session: AsyncSession = Depends(get_db_session),
) -> CareersRepository:
    """Get careers repository instance."""
    return CareersRepository(session)


async def get_careers_service(
    repository: CareersRepository = Depends(get_careers_repository),
) -> CareersService:
    """Get careers service instance with injected dependencies."""
    return CareersService(repository)
