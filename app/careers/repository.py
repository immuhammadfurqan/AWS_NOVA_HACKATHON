"""
Careers Repository

Database access layer for public job listings.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.jobs.models import JobRecord
from app.jobs.schemas.enums import ApprovalStatus


class CareersRepository:
    """Repository for public careers data access."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_approved_jobs(self) -> list[JobRecord]:
        """Get all jobs with approved JDs for public display."""
        result = await self.session.execute(
            select(JobRecord)
            .where(JobRecord.jd_approval_status == ApprovalStatus.APPROVED.value)
            .order_by(JobRecord.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_public_job(self, job_id: UUID) -> JobRecord | None:
        """Get a single job by ID if it's approved for public display."""
        result = await self.session.execute(
            select(JobRecord)
            .where(JobRecord.id == job_id)
            .where(JobRecord.jd_approval_status == ApprovalStatus.APPROVED.value)
        )
        return result.scalar_one_or_none()
