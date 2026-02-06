"""
Candidates App Services

Orchestration layer for candidate-related business operations.
Uses CandidateRepository for database access.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.config import Settings
from app.core.exceptions import RecordNotFoundError, ValidationError
from app.core.logging import get_logger

from app.candidates.models import ApplicantRecord
from app.candidates.repository import CandidateRepository
from app.candidates.schemas import (
    Applicant,
    CandidateResponsesResponse,
    CandidateResponse,
    ScheduleInterviewRequest,
)
from app.jobs.schemas import GeneratedJD


class CandidateService:
    """
    Service layer for candidate-related operations.

    Coordinates between CandidateRepository and business logic.
    All dependencies are injected for testability.
    """

    def __init__(
        self,
        session: AsyncSession,
        settings: Settings,
        repository: CandidateRepository,
    ) -> None:
        """
        Initialize CandidateService with dependencies.

        Args:
            session: Database session
            settings: Application settings
            repository: CandidateRepository for DB operations
        """
        self.session = session
        self.settings = settings
        self.repository = repository
        self.logger = get_logger(__name__)

    def _log_operation(self, operation: str, success: bool, details: dict = None):
        """Log an operation with its outcome."""
        if details is None:
            details = {}
        status = "success" if success else "failed"
        self.logger.info(f"Operation {operation} {status}", extra=details)

    async def get_applicants(self, job_id: str) -> dict:
        """Get all applicants for a job."""
        applicants_db = await self.repository.get_applicants_by_job(UUID(job_id))

        applicants = []
        shortlisted = []

        for rec in applicants_db:
            app_schema = Applicant(
                id=rec.id,
                name=rec.name,
                email=rec.email,
                phone=rec.phone,
                resume_path=rec.resume_path,
                resume_text=rec.resume_text,
                embedding=None,  # Loaded from Pinecone if needed
                similarity_score=rec.similarity_score,
                shortlisted=rec.shortlisted,
                applied_at=rec.applied_at,
            )
            applicants.append(app_schema)
            if rec.shortlisted:
                shortlisted.append(rec.id)

        return {
            "total": len(applicants),
            "applicants": applicants,
            "shortlisted": shortlisted,
        }

    async def get_all_candidates(self) -> dict:
        """
        Get all candidates across all jobs.

        Returns candidates with their associated job title for the global view.
        """

        # Query all applicants with their job relationship
        result = await self.session.execute(
            select(ApplicantRecord)
            .options(joinedload(ApplicantRecord.job))
            .order_by(ApplicantRecord.applied_at.desc())
        )
        applicants_db = result.scalars().unique().all()

        candidates = []
        for rec in applicants_db:
            # Get job title from generated_jd
            job_title = "Unknown Position"
            if rec.job and rec.job.generated_jd:
                try:
                    jd = GeneratedJD.model_validate(rec.job.generated_jd)
                    job_title = jd.job_title
                except Exception:
                    pass

            candidates.append(
                {
                    "id": str(rec.id),
                    "name": rec.name,
                    "email": rec.email,
                    "phone": rec.phone,
                    "resume_path": rec.resume_path,
                    "similarity_score": (
                        rec.similarity_score * 100 if rec.similarity_score else 0
                    ),
                    "shortlisted": rec.shortlisted,
                    "applied_at": (
                        rec.applied_at.isoformat() if rec.applied_at else None
                    ),
                    "job_id": str(rec.job_id),
                    "job_title": job_title,
                }
            )

        return {
            "total": len(candidates),
            "candidates": candidates,
        }

    async def get_candidate_responses(
        self, job_id: str, candidate_id: str
    ) -> CandidateResponsesResponse:
        """Get prescreening responses for a candidate."""
        # Get Candidate
        candidate = await self.repository.get_applicant_by_id(
            UUID(job_id), UUID(candidate_id)
        )
        if not candidate:
            raise RecordNotFoundError("Candidate", candidate_id)

        # Get Responses
        responses_db = await self.repository.get_prescreening_responses(
            UUID(candidate_id)
        )

        responses = [
            CandidateResponse(
                id=r.id,
                candidate_id=r.candidate_id,
                question_id=r.question_id,
                question_text=r.question_text,
                transcript=r.transcript,
                audio_url=r.audio_url,
                ai_score=r.ai_score,
                scoring_rationale=r.scoring_rationale,
                call_duration_seconds=r.call_duration_seconds,
                recorded_at=r.recorded_at,
            )
            for r in responses_db
        ]

        # Calculate scores
        total_score = sum(r.ai_score for r in responses)
        max_score = len(responses) * 100
        percentage = (total_score / max_score * 100) if max_score > 0 else 0

        self.logger.info(f"Retrieved responses for candidate {candidate_id}")

        return CandidateResponsesResponse(
            candidate_id=candidate.id,
            candidate_name=candidate.name,
            candidate_email=candidate.email,
            total_score=total_score,
            max_possible_score=max_score,
            percentage_score=percentage,
            responses=responses,
        )

    async def schedule_interview(
        self,
        job_id: str,
        candidate_id: str,
        request: ScheduleInterviewRequest,
    ) -> dict:
        """Schedule an interview for a candidate."""
        candidate = await self.repository.get_applicant_by_id(
            UUID(job_id), UUID(candidate_id)
        )

        if not candidate:
            raise RecordNotFoundError("Candidate", candidate_id)

        if not candidate.shortlisted:
            raise ValidationError(
                message="Candidate is not shortlisted", field="candidate_id"
            )

        self._log_operation(
            "schedule_interview",
            success=True,
            details={"candidate_id": candidate_id},
        )

        return {
            "message": "Interview scheduling initiated",
            "interviewer_email": request.interviewer_email,
            "preferred_datetime": request.preferred_datetime.isoformat(),
        }

    async def reject_candidate(
        self, job_id: str, candidate_id: str, reason: Optional[str]
    ) -> dict:
        """Reject a candidate."""
        candidate = await self.repository.get_applicant_by_id(
            UUID(job_id), UUID(candidate_id)
        )

        if not candidate:
            raise RecordNotFoundError("Candidate", candidate_id)

        await self.repository.update_shortlist_status(
            UUID(job_id), UUID(candidate_id), shortlisted=False
        )

        self._log_operation(
            "reject_candidate",
            success=True,
            details={"candidate_id": candidate_id, "reason": reason},
        )

        return {"message": f"Candidate {candidate_id} rejected", "reason": reason}
