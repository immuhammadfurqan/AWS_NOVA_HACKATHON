"""
Request schemas for Jobs API endpoints.
"""

from pydantic import BaseModel, Field

from app.jobs.schemas.fields import (
    JobTitle,
    LocationSalaryMixin,
)


class JDUpdateRequest(LocationSalaryMixin):
    """
    Request to manually update a generated JD.

    All fields are optional to allow partial updates.
    """

    job_title: JobTitle | None = None
    summary: str | None = Field(default=None, min_length=50, max_length=1000)
    description: str | None = Field(default=None, min_length=100, max_length=10000)
    responsibilities: list[str] | None = Field(default=None, max_length=20)
    requirements: list[str] | None = Field(default=None, max_length=30)
    nice_to_have: list[str] | None = Field(default=None, max_length=20)
    benefits: list[str] | None = Field(default=None, max_length=30)


class JDRegenerateRequest(BaseModel):
    """Request to regenerate JD with feedback."""

    feedback: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Recruiter feedback for AI to incorporate",
        examples=[
            "Make it more concise and focus on technical skills",
            "Emphasize remote work opportunities and work-life balance",
            "Add more details about the team structure",
        ],
    )
