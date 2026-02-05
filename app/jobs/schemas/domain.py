"""
Domain models for Jobs module.

Core business entities: JobInput and GeneratedJD.
"""

from pydantic import BaseModel, Field, field_validator

from app.jobs.schemas.fields import (
    JobTitle,
    CompanyName,
    Department,
    ExperienceYears,
    SkillsList,
    LocationSalaryMixin,
)


class JobInput(LocationSalaryMixin):
    """
    Raw input from recruiter to start a recruitment process.

    Validates all inputs to ensure data quality.
    """

    role_title: JobTitle
    department: Department
    company_name: CompanyName
    company_description: str | None = Field(
        default=None,
        max_length=2000,
        description="Brief description of the company",
    )
    key_requirements: SkillsList
    nice_to_have: SkillsList
    experience_years: ExperienceYears = 3
    prescreening_questions: list[str] = Field(
        default_factory=list,
        max_length=10,
        description="Custom prescreening questions for voice calls (max 10)",
    )

    @field_validator("key_requirements", "nice_to_have", "prescreening_questions")
    @classmethod
    def validate_non_empty_strings(cls, v: list[str]) -> list[str]:
        """Remove empty strings and trim whitespace."""
        return [item.strip() for item in v if item.strip()]

    @field_validator("prescreening_questions")
    @classmethod
    def validate_question_length(cls, v: list[str]) -> list[str]:
        """Ensure questions are not too short or too long."""
        for question in v:
            if len(question) < 10:
                raise ValueError("Questions must be at least 10 characters")
            if len(question) > 500:
                raise ValueError("Questions must be at most 500 characters")
        return v


class GeneratedJD(LocationSalaryMixin):
    """
    Structured job description output from AI.

    Comprehensive validation ensures quality outputs.
    """

    job_title: JobTitle
    summary: str = Field(
        ...,
        min_length=50,
        max_length=1000,
        description="Brief role summary (2-3 sentences)",
    )
    description: str = Field(
        ...,
        min_length=100,
        max_length=10000,
        description="Full job description",
    )
    responsibilities: list[str] = Field(
        default_factory=list,
        max_length=20,
        description="Key responsibilities",
    )
    requirements: list[str] = Field(
        default_factory=list,
        max_length=30,
        description="Required qualifications",
    )
    nice_to_have: list[str] = Field(
        default_factory=list,
        max_length=20,
        description="Preferred qualifications",
    )
    benefits: list[str] = Field(
        default_factory=list,
        max_length=30,
        description="Benefits and perks",
    )
    seo_keywords: list[str] = Field(
        default_factory=list,
        max_length=20,
        description="Keywords for search optimization",
    )

    @field_validator("responsibilities", "requirements", "nice_to_have", "benefits")
    @classmethod
    def validate_list_items(cls, v: list[str]) -> list[str]:
        """Ensure list items are meaningful."""
        cleaned = [item.strip() for item in v if item.strip()]
        for item in cleaned:
            if len(item) < 5:
                raise ValueError("List items must be at least 5 characters")
        return cleaned
