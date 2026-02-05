"""
Candidate Repository

Data access layer for Candidate-related database operations.
Follows the Repository pattern for clean separation of concerns.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.candidates.models import ApplicantRecord, PrescreeningResponseRecord


class CandidateRepository:
    """
    Repository for Candidate database operations.

    Encapsulates all data access logic for ApplicantRecord
    and PrescreeningResponseRecord.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize the repository with a database session.

        Args:
            session: SQLAlchemy async session (injected via DI)
        """
        self.session = session

    async def get_applicants_by_job(self, job_id: UUID) -> List[ApplicantRecord]:
        """
        Get all applicants for a specific job.

        Args:
            job_id: The UUID of the job

        Returns:
            List of ApplicantRecord instances
        """
        result = await self.session.execute(
            select(ApplicantRecord).where(ApplicantRecord.job_id == job_id)
        )
        return list(result.scalars().all())

    async def get_applicant_by_id(
        self, job_id: UUID, candidate_id: UUID
    ) -> Optional[ApplicantRecord]:
        """
        Get a specific applicant by job and candidate ID.

        Args:
            job_id: The UUID of the job
            candidate_id: The UUID of the candidate

        Returns:
            ApplicantRecord if found, None otherwise
        """
        result = await self.session.execute(
            select(ApplicantRecord).where(
                ApplicantRecord.id == candidate_id,
                ApplicantRecord.job_id == job_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_prescreening_responses(
        self, candidate_id: UUID
    ) -> List[PrescreeningResponseRecord]:
        """
        Get all prescreening responses for a candidate.

        Args:
            candidate_id: The UUID of the candidate

        Returns:
            List of PrescreeningResponseRecord instances
        """
        result = await self.session.execute(
            select(PrescreeningResponseRecord).where(
                PrescreeningResponseRecord.candidate_id == candidate_id
            )
        )
        return list(result.scalars().all())

    async def update_shortlist_status(
        self, job_id: UUID, candidate_id: UUID, shortlisted: bool
    ) -> None:
        """
        Update the shortlist status of a candidate.

        Args:
            job_id: The UUID of the job
            candidate_id: The UUID of the candidate
            shortlisted: Whether the candidate is shortlisted
        """
        await self.session.execute(
            update(ApplicantRecord)
            .where(
                ApplicantRecord.id == candidate_id,
                ApplicantRecord.job_id == job_id,
            )
            .values(shortlisted=shortlisted)
        )
        await self.session.commit()
