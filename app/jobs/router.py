"""
Jobs App Router (API Routes)

Thin HTTP layer that delegates to the service layer.
Contains no business logic, locking, or background task definitions.
"""

from fastapi import APIRouter, Depends, BackgroundTasks

from app.jobs.dependencies import get_job_service
from app.jobs.services import JobService
from app.jobs.schemas import (
    JobInput,
    JobCreateResponse,
    JobStatusResponse,
    JDUpdateRequest,
    JDRegenerateRequest,
    JDApprovalResponse,
    ShortlistApprovalResponse,
    MockApplicantsResponse,
    DeleteJobResponse,
    JobListResponse,
)
from app.core.logging import get_logger
from app.auth.models import User
from app.auth.jwt_dependencies import get_current_user

router = APIRouter(prefix="/jobs", tags=["Jobs"])
logger = get_logger(__name__)


@router.get(
    "/",
    response_model=JobListResponse,
    summary="List all jobs for current user",
)
async def list_jobs(
    service: JobService = Depends(get_job_service),
    user: User = Depends(get_current_user),
):
    """List all jobs created by the current user."""
    return await service.list_jobs(user)


@router.post(
    "/create",
    response_model=JobCreateResponse,
    summary="Create a new recruitment process",
)
async def create_job(
    job_input: JobInput,
    background_tasks: BackgroundTasks,
    service: JobService = Depends(get_job_service),
    user: User = Depends(get_current_user),
):
    """
    Create a new recruitment process.

    This triggers the LangGraph workflow starting with JD generation.
    """
    response = await service.create_job(job_input, user)

    # Schedule background graph execution
    state = await service.get_job_state(str(response.job_id))
    background_tasks.add_task(
        service.execute_graph_background, str(response.job_id), state
    )

    return response


@router.get(
    "/status/{job_id}",
    response_model=JobStatusResponse,
    summary="Get recruitment process status",
)
async def get_job_status(
    job_id: str,
    service: JobService = Depends(get_job_service),
    user: User = Depends(get_current_user),
):
    """Get the current status of a recruitment process."""
    return await service.get_job_status(job_id, user)


@router.get(
    "/{job_id}/jd",
    summary="Get generated job description",
)
async def get_generated_jd(
    job_id: str,
    service: JobService = Depends(get_job_service),
    user: User = Depends(get_current_user),
):
    """Get the AI-generated job description."""
    jd = await service.get_generated_jd(job_id, user)
    return jd.model_dump()


@router.post(
    "/{job_id}/approve-jd",
    response_model=JDApprovalResponse,
    summary="Approve generated job description",
)
async def approve_jd(
    job_id: str,
    service: JobService = Depends(get_job_service),
    user: User = Depends(get_current_user),
):
    """Approve the generated JD and trigger posting."""
    return await service.approve_jd(job_id, user)


@router.put(
    "/{job_id}/jd",
    summary="Update generated job description manually",
)
async def update_jd(
    job_id: str,
    jd_update: JDUpdateRequest,
    service: JobService = Depends(get_job_service),
    user: User = Depends(get_current_user),
):
    """Manually update the generated JD fields."""
    updated_jd = await service.update_jd(
        job_id, jd_update.model_dump(exclude_unset=True), user
    )
    return updated_jd.model_dump()


@router.post(
    "/{job_id}/regenerate-jd",
    summary="Regenerate JD with AI using feedback",
)
async def regenerate_jd(
    job_id: str,
    request: JDRegenerateRequest,
    service: JobService = Depends(get_job_service),
    user: User = Depends(get_current_user),
):
    """Regenerate the JD using AI with recruiter feedback."""
    new_jd = await service.regenerate_jd(job_id, request.feedback, user)
    return new_jd.model_dump()


@router.post(
    "/{job_id}/approve-shortlist",
    response_model=ShortlistApprovalResponse,
    summary="Approve shortlisted candidates",
)
async def approve_shortlist(
    job_id: str,
    background_tasks: BackgroundTasks,
    service: JobService = Depends(get_job_service),
    user: User = Depends(get_current_user),
):
    """Approve the shortlisted candidates."""
    result = await service.approve_shortlist(job_id, user)

    # Resume graph execution in background
    state = await service.get_job_state(job_id)
    background_tasks.add_task(service.execute_graph_background, job_id, state)

    return result


@router.post(
    "/{job_id}/mock/add-applicants",
    response_model=MockApplicantsResponse,
    summary="Add mock applicants",
)
async def add_mock_applicants(
    job_id: str,
    count: int = 5,
    service: JobService = Depends(get_job_service),
    user: User = Depends(get_current_user),
):
    """Add mock applicants for testing (debug only)."""
    return await service.add_mock_applicants(job_id, user, count)


@router.delete(
    "/{job_id}",
    response_model=DeleteJobResponse,
    summary="Delete a recruitment process",
)
async def delete_job(
    job_id: str,
    service: JobService = Depends(get_job_service),
    user: User = Depends(get_current_user),
):
    """
    Delete a recruitment process and all associated data.

    This includes:
    - Database records
    - Pinecone embeddings (JD and candidates)
    """
    return await service.delete_job(job_id, user)
