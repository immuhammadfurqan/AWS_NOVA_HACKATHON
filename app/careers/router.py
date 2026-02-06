"""
Careers Router

Public job listing endpoints for Google indexing and careers pages.
These endpoints do NOT require authentication.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, Form, File, UploadFile

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


@router.post(
    "/{job_id}/apply",
    summary="Apply for a job",
)
async def apply_for_job(
    job_id: UUID,
    name: str = Form(
        ..., min_length=2, max_length=100, description="Applicant full name"
    ),
    email: str = Form(..., description="Applicant email address"),
    phone: str | None = Form(
        default=None, max_length=20, description="Phone number (optional)"
    ),
    resume: UploadFile = File(..., description="Resume file (PDF only, max 10MB)"),
    service: CareersService = Depends(get_careers_service),
):
    """
    Submit a job application with resume (public endpoint, no auth required).

    - Accepts multipart/form-data
    - Resume must be a PDF file (max 10MB)
    - Returns applicant_id on success
    - Automatically calculates resume-JD similarity score
    """
    # Validate file type
    if not resume.filename or not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Resume must be a PDF file")

    # Validate file size (10MB limit)
    content = await resume.read()
    max_size = 10 * 1024 * 1024  # 10MB
    if len(content) > max_size:
        raise HTTPException(
            status_code=400, detail="Resume file too large. Maximum size is 10MB."
        )

    try:
        result = await service.create_application(
            job_id=job_id,
            name=name,
            email=email,
            phone=phone,
            resume_content=content,
            resume_filename=resume.filename,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
