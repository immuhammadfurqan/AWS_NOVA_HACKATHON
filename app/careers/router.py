"""
Careers Router

Public job listing endpoints for Google indexing and careers pages.
These endpoints do NOT require authentication.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response

from app.careers.dependencies import get_careers_service
from app.careers.service import CareersService
from app.jobs.schemas import (
    PublicJobListItem,
    PublicJobListResponse,
    PublicJobResponse,
)

router = APIRouter(prefix="/careers", tags=["Public Careers"])


@router.get(
    "/",
    response_model=PublicJobListResponse,
    summary="List all public job openings",
)
async def list_public_jobs(
    service: CareersService = Depends(get_careers_service),
):
    """
    List all approved/posted jobs for public viewing.

    This endpoint is unauthenticated and intended for:
    - Public careers pages
    - Google for Jobs crawler
    """
    job_items, total = await service.list_public_jobs()

    return PublicJobListResponse(
        jobs=[PublicJobListItem(**job) for job in job_items],
        total=total,
    )


@router.get(
    "/feed",
    summary="Get XML feed for job boards",
    response_class=Response,
)
async def get_job_feed(
    service: CareersService = Depends(get_careers_service),
):
    """
    Get XML feed of all jobs for integration with Indeed/LinkedIn.
    Success response is application/xml.
    """
    xml_content = await service.generate_feed()
    return Response(content=xml_content, media_type="application/xml")


@router.get(
    "/{job_id}",
    response_model=PublicJobResponse,
    summary="Get public job details with JSON-LD",
)
async def get_public_job(
    job_id: UUID,
    service: CareersService = Depends(get_careers_service),
):
    """
    Get full job details for public viewing.

    Returns:
    - Complete job description
    - JSON-LD structured data for Google indexing

    This endpoint should be embedded in public job pages.
    """
    job_detail = await service.get_public_job_detail(job_id)

    if not job_detail:
        raise HTTPException(status_code=404, detail="Job not found")

    return PublicJobResponse(**job_detail)
