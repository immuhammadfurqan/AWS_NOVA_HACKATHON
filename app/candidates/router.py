"""
Candidates App Router (API Routes)
"""

from typing import Optional
from fastapi import APIRouter, Depends, BackgroundTasks

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.config import get_settings, Settings
from app.candidates.services import CandidateService
from app.candidates.repository import CandidateRepository
from app.candidates.schemas import CandidateResponsesResponse, ScheduleInterviewRequest

router = APIRouter()


def get_candidate_repository(
    session: AsyncSession = Depends(get_db_session),
) -> CandidateRepository:
    """Provide a CandidateRepository instance."""
    return CandidateRepository(session)


async def get_candidate_service(
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
    repository: CandidateRepository = Depends(get_candidate_repository),
) -> CandidateService:
    """Dependency to get CandidateService instance with injected dependencies."""
    return CandidateService(session, settings, repository)


# Note: These routes are related to jobs, so the path includes /jobs/{job_id}
# We will likely mount this router at root or handle prefixing in main.py


@router.get(
    "/jobs/{job_id}/applicants",
    summary="List all applicants",
    tags=["Candidates"],
)
async def get_applicants(
    job_id: str,
    service: CandidateService = Depends(get_candidate_service),
):
    """Get all applicants for a job."""
    return await service.get_applicants(job_id)


@router.get(
    "/jobs/{job_id}/candidates/{candidate_id}/responses",
    response_model=CandidateResponsesResponse,
    summary="Get prescreening responses",
    tags=["Candidates"],
)
async def get_candidate_responses(
    job_id: str,
    candidate_id: str,
    service: CandidateService = Depends(get_candidate_service),
):
    """
    Get prescreening responses for a candidate.

    Returns transcripts, AI scores, and audio URLs.
    """
    return await service.get_candidate_responses(job_id, candidate_id)


@router.post(
    "/jobs/{job_id}/candidates/{candidate_id}/schedule",
    summary="Schedule technical interview",
    tags=["Candidates"],
)
async def schedule_interview(
    job_id: str,
    candidate_id: str,
    request: ScheduleInterviewRequest,
    background_tasks: BackgroundTasks,
    service: CandidateService = Depends(get_candidate_service),
):
    """
    Schedule a technical interview for a candidate.

    Creates a Google Calendar event and sends invites.
    """
    # Note: Logic for calendar interaction handles in service or background?
    # Original code called 'candidate_service.schedule_interview'.
    # We follow that pattern.
    return await service.schedule_interview(job_id, candidate_id, request)


@router.post(
    "/jobs/{job_id}/candidates/{candidate_id}/reject",
    summary="Reject candidate",
    tags=["Candidates"],
)
async def reject_candidate(
    job_id: str,
    candidate_id: str,
    reason: Optional[str] = None,
    service: CandidateService = Depends(get_candidate_service),
):
    """Reject a candidate after prescreening."""
    return await service.reject_candidate(job_id, candidate_id, reason)
