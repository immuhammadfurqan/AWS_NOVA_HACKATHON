"""
Response schemas for Jobs API endpoints.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.jobs.schemas.enums import RecruitmentNodeStatus, ApprovalStatus


# ============================================================================
# BASE RESPONSE
# ============================================================================


class BaseOperationResponse(BaseModel):
    """Base class for operation responses."""

    message: str = Field(..., description="Human-readable operation result")


# ============================================================================
# JOB RESPONSES
# ============================================================================


class JobCreateResponse(BaseModel):
    """Response after creating a new job recruitment process."""

    job_id: UUID
    thread_id: str
    message: str = "Recruitment process started"
    current_node: RecruitmentNodeStatus


class JobStatusResponse(BaseModel):
    """Response for job status queries."""

    job_id: UUID
    current_node: RecruitmentNodeStatus
    jd_approval_status: ApprovalStatus
    applicant_count: int = Field(ge=0)
    shortlisted_count: int = Field(ge=0)
    shortlist_approval_status: ApprovalStatus
    prescreening_complete: bool
    scheduled_interviews_count: int = Field(ge=0)
    has_generated_jd: bool = False
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime


# ============================================================================
# OPERATION RESPONSES
# ============================================================================


class JDApprovalResponse(BaseOperationResponse):
    """Response for JD approval."""

    job_id: str = Field(..., description="ID of the approved job")


class ShortlistApprovalResponse(BaseOperationResponse):
    """Response for shortlist approval."""

    shortlisted_count: int = Field(ge=0, description="Number of shortlisted candidates")


class MockApplicantsResponse(BaseOperationResponse):
    """Response for adding mock applicants."""

    total_applicants: int = Field(ge=0, description="Total number of applicants")


class DeleteJobResponse(BaseOperationResponse):
    """Response for job deletion."""

    pass  # Only needs message from base class


# ============================================================================
# LIST RESPONSES
# ============================================================================


class JobListItem(BaseModel):
    """Individual job item in list response."""

    job_id: UUID
    role_title: str
    company_name: str
    current_node: RecruitmentNodeStatus
    created_at: datetime
    updated_at: datetime


class JobListResponse(BaseModel):
    """Response for listing all jobs."""

    jobs: list[JobListItem]
    total: int = Field(ge=0, description="Total number of jobs")


# ============================================================================
# PUBLIC JOB RESPONSES (for Google for Jobs / Careers Pages)
# ============================================================================


class PublicJobListItem(BaseModel):
    """Public job listing item (no sensitive data)."""

    job_id: UUID
    job_title: str
    company_name: str
    location: str | None = None
    salary_range: str | None = None
    summary: str
    posted_at: datetime


class PublicJobResponse(BaseModel):
    """Public job detail with JSON-LD for Google indexing."""

    job_id: UUID
    job_title: str
    company_name: str
    company_description: str | None = None
    location: str | None = None
    salary_range: str | None = None
    summary: str
    description: str
    responsibilities: list[str]
    requirements: list[str]
    nice_to_have: list[str]
    benefits: list[str]
    posted_at: datetime
    jsonld: dict  # The JSON-LD structured data for embedding


class PublicJobListResponse(BaseModel):
    """Response for public job listings."""

    jobs: list[PublicJobListItem]
    total: int = Field(ge=0)
