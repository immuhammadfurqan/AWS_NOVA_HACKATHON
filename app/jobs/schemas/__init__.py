"""
Jobs Schemas Package.

Re-exports all schemas for backward compatibility.
Usage: from app.jobs.schemas import JobInput, GeneratedJD, ...
"""

from app.jobs.schemas.enums import (
    RecruitmentNodeStatus,
    ApprovalStatus,
)
from app.jobs.schemas.fields import (
    JobTitle,
    CompanyName,
    Department,
    LocationStr,
    SalaryRange,
    ExperienceYears,
    SkillsList,
    LocationSalaryMixin,
)
from app.jobs.schemas.domain import (
    JobInput,
    GeneratedJD,
)
from app.jobs.schemas.requests import (
    JDUpdateRequest,
    JDRegenerateRequest,
)
from app.jobs.schemas.responses import (
    BaseOperationResponse,
    JobCreateResponse,
    JobStatusResponse,
    JDApprovalResponse,
    ShortlistApprovalResponse,
    MockApplicantsResponse,
    DeleteJobResponse,
    JobListItem,
    JobListResponse,
    PublicJobListItem,
    PublicJobResponse,
    PublicJobListResponse,
)

__all__ = [
    # Enums
    "RecruitmentNodeStatus",
    "ApprovalStatus",
    # Fields
    "JobTitle",
    "CompanyName",
    "Department",
    "LocationStr",
    "SalaryRange",
    "ExperienceYears",
    "SkillsList",
    "LocationSalaryMixin",
    # Domain
    "JobInput",
    "GeneratedJD",
    # Requests
    "JDUpdateRequest",
    "JDRegenerateRequest",
    # Responses
    "BaseOperationResponse",
    "JobCreateResponse",
    "JobStatusResponse",
    "JDApprovalResponse",
    "ShortlistApprovalResponse",
    "MockApplicantsResponse",
    "DeleteJobResponse",
    "JobListItem",
    "JobListResponse",
    "PublicJobListItem",
    "PublicJobResponse",
    "PublicJobListResponse",
]
