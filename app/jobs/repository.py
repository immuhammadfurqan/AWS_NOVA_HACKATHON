"""
Job Repository

Data access layer for Job-related database operations.
Implements the Repository pattern for clean separation of concerns.
"""

from datetime import datetime, timezone
from uuid import UUID
from typing import Optional

from sqlalchemy import update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.jobs.models import JobRecord


class JobRepository:
    """
    Repository for JobRecord database operations.

    Follows the Repository pattern to encapsulate data access logic,
    making the service layer agnostic to the underlying storage.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize the repository with a database session.

        Args:
            session: SQLAlchemy async session (injected via DI)
        """
        self.session = session

    async def create(self, job_record: JobRecord) -> JobRecord:
        """
        Persist a new job record to the database.

        Args:
            job_record: The JobRecord instance to persist

        Returns:
            The persisted JobRecord with any DB-generated fields populated
        """
        self.session.add(job_record)
        await self.session.commit()
        await self.session.refresh(job_record)
        return job_record

    async def get_by_id(self, job_id: UUID) -> Optional[JobRecord]:
        """
        Retrieve a job record by its ID.

        Args:
            job_id: The UUID of the job to retrieve

        Returns:
            The JobRecord if found, None otherwise
        """
        result = await self.session.execute(
            select(JobRecord).where(JobRecord.id == job_id)
        )
        return result.scalar_one_or_none()

    async def update(self, job_id: UUID, **values) -> None:
        """
        Update a job record with the given values.

        Args:
            job_id: The UUID of the job to update
            **values: Key-value pairs of fields to update
        """
        values["updated_at"] = datetime.now(timezone.utc)
        await self.session.execute(
            update(JobRecord).where(JobRecord.id == job_id).values(**values)
        )
        await self.session.commit()

    async def delete(self, job_id: UUID) -> int:
        """
        Delete a job record by its ID.

        Args:
            job_id: The UUID of the job to delete

        Returns:
            The number of rows deleted (0 or 1)
        """
        result = await self.session.execute(
            delete(JobRecord).where(JobRecord.id == job_id)
        )
        await self.session.commit()
        return result.rowcount

    async def get_by_user_id(self, user_id: UUID) -> list[JobRecord]:
        """
        Retrieve all jobs for a specific user, ordered by created_at desc.

        Args:
            user_id: The UUID of the user whose jobs to retrieve

        Returns:
            List of JobRecord instances belonging to the user
        """
        result = await self.session.execute(
            select(JobRecord)
            .where(JobRecord.owner_id == user_id)
            .order_by(JobRecord.created_at.desc())
        )
        return list(result.scalars().all())
