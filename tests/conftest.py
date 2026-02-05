"""
AARLP Test Configuration

Pytest fixtures and configuration for testing.
"""

import asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.core.config import Settings
from app.main import app
from app.jobs.schemas import (
    JobInput,
    GeneratedJD,
)
from app.candidates.schemas import Applicant
from app.interviews.schemas import PrescreeningQuestion


# ============================================================================
# Event Loop Configuration
# ============================================================================

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Settings Fixtures
# ============================================================================

@pytest.fixture
def test_settings() -> Settings:
    """Get test settings with debug enabled."""
    return Settings(
        debug=True,
        database_url="postgresql+asyncpg://test:test@localhost:5432/aarlp_test",
        openai_api_key="test-key",
        voice_provider="mock",
    )


# ============================================================================
# Client Fixtures
# ============================================================================

@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Get a synchronous test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Get an async test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# ============================================================================
# Model Fixtures
# ============================================================================

@pytest.fixture
def sample_job_input() -> JobInput:
    """Create a sample job input for testing."""
    return JobInput(
        role_title="Senior Backend Engineer",
        department="Engineering",
        company_name="TechCorp Inc.",
        company_description="A leading technology company",
        key_requirements=["Python", "FastAPI", "PostgreSQL", "Docker"],
        nice_to_have=["Kubernetes", "AWS", "GraphQL"],
        experience_years=5,
        location="Remote",
        salary_range="$150,000 - $200,000",
        prescreening_questions=[
            "Tell me about your experience with Python.",
            "Describe a challenging bug you fixed.",
            "How do you approach system design?",
        ],
    )


@pytest.fixture
def sample_generated_jd() -> GeneratedJD:
    """Create a sample generated JD for testing."""
    return GeneratedJD(
        job_title="Senior Backend Engineer",
        summary="Join our world-class engineering team...",
        description="We are looking for a talented Senior Backend Engineer...",
        responsibilities=[
            "Design and implement scalable APIs",
            "Collaborate with cross-functional teams",
            "Mentor junior engineers",
        ],
        requirements=[
            "5+ years Python experience",
            "Strong FastAPI knowledge",
            "PostgreSQL expertise",
        ],
        nice_to_have=["Kubernetes experience", "AWS certification"],
        benefits=["Competitive salary", "Remote work", "Health insurance"],
        seo_keywords=["python", "backend", "senior engineer", "remote"],
        salary_range="$150,000 - $200,000",
        location="Remote",
    )


@pytest.fixture
def sample_applicants() -> list[Applicant]:
    """Create sample applicants for testing."""
    return [
        Applicant(
            id=uuid4(),
            name="Alice Johnson",
            email="alice@example.com",
            phone="+15551234567",
            resume_text="Experienced Python developer with 6 years...",
        ),
        Applicant(
            id=uuid4(),
            name="Bob Smith",
            email="bob@example.com",
            phone="+15559876543",
            resume_text="Backend engineer specializing in FastAPI...",
        ),
        Applicant(
            id=uuid4(),
            name="Carol Williams",
            email="carol@example.com",
            phone="+15555555555",
            resume_text="Full-stack developer with Python and React...",
        ),
    ]


@pytest.fixture
def sample_prescreening_questions() -> list[PrescreeningQuestion]:
    """Create sample prescreening questions for testing."""
    return [
        PrescreeningQuestion(
            question_text="Tell me about your Python experience.",
            expected_keywords=["python", "django", "fastapi", "flask", "async"],
            max_score=100,
        ),
        PrescreeningQuestion(
            question_text="Describe a challenging bug you fixed.",
            expected_keywords=["debugging", "root cause", "investigation", "fix"],
            max_score=100,
        ),
    ]


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "choices": [
            {
                "message": {
                    "content": '{"score": 85, "rationale": "Strong technical answer"}'
                }
            }
        ]
    }
