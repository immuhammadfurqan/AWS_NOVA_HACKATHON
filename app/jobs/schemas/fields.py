"""
Reusable field types and mixins for Jobs schemas.

Following DRY principle with Annotated types.
"""

from typing import Annotated

from pydantic import BaseModel, Field


# ============================================================================
# REUSABLE FIELD TYPES
# ============================================================================

JobTitle = Annotated[
    str,
    Field(
        min_length=3,
        max_length=100,
        description="Job title",
        examples=["Senior Backend Engineer", "Product Manager"],
    ),
]

CompanyName = Annotated[
    str,
    Field(
        min_length=2,
        max_length=100,
        description="Company name",
        examples=["TechCorp Inc.", "Startup XYZ"],
    ),
]

Department = Annotated[
    str,
    Field(
        min_length=2,
        max_length=100,
        description="Department or team",
        examples=["Engineering", "Product", "Marketing"],
    ),
]

LocationStr = Annotated[
    str | None,
    Field(
        default=None,
        max_length=200,
        description="Job location or 'Remote'",
        examples=["Remote", "New York, NY", "San Francisco, CA"],
    ),
]

SalaryRange = Annotated[
    str | None,
    Field(
        default=None,
        max_length=100,
        description="Salary range for the position",
        examples=["$120,000 - $180,000", "$100k - $150k"],
    ),
]

ExperienceYears = Annotated[
    int,
    Field(
        ge=0,
        le=50,
        description="Years of experience",
        examples=[3, 5, 10],
    ),
]

SkillsList = Annotated[
    list[str],
    Field(
        default_factory=list,
        max_length=50,
        description="List of skills or qualifications",
        examples=[["Python", "FastAPI", "PostgreSQL"]],
    ),
]


# ============================================================================
# MIXINS
# ============================================================================


class LocationSalaryMixin(BaseModel):
    """Mixin for location and salary fields (DRY)."""

    location: LocationStr = None
    salary_range: SalaryRange = None
