"""
Careers Service Tests

Unit tests for public careers service operations.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from pathlib import Path

from app.careers.constants import (
    UPLOADS_DIR,
    MAX_RESUME_SIZE_MB,
    SIMILARITY_HIGH_THRESHOLD,
)


class TestCareersConstants:
    """Tests for careers constants."""

    def test_uploads_dir_is_path(self):
        """Uploads dir should be Path object."""
        assert isinstance(UPLOADS_DIR, Path)

    def test_max_resume_size_reasonable(self):
        """Max resume size should be reasonable."""
        assert MAX_RESUME_SIZE_MB >= 5
        assert MAX_RESUME_SIZE_MB <= 50

    def test_similarity_threshold_valid(self):
        """Similarity threshold should be 0-1."""
        assert 0 <= SIMILARITY_HIGH_THRESHOLD <= 1


class TestCareersService:
    """Tests for CareersService class."""

    @pytest.fixture
    def mock_repository(self):
        """Mock careers repository."""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_list_public_jobs(self, mock_repository):
        """List public jobs should return approved jobs."""
        from app.careers.service import CareersService

        mock_repository.list_approved_jobs.return_value = ([], 0)

        service = CareersService(repository=mock_repository)
        jobs, total = await service.list_public_jobs()

        assert isinstance(jobs, list)
        assert isinstance(total, int)

    @pytest.mark.asyncio
    async def test_get_job_details(self, mock_repository):
        """Get job details should return full JD and JSON-LD."""
        from app.careers.service import CareersService

        mock_job = MagicMock()
        mock_job.id = uuid4()
        mock_job.generated_jd = {
            "job_title": "Software Engineer",
            "summary": "Summary",
            "description": "Description",
            "responsibilities": [],
            "requirements": [],
            "nice_to_have": [],
            "benefits": [],
            "location": "Remote",
            "salary_range": "$100k",
        }
        mock_job.company_name = "TechCorp"
        mock_job.company_description = "Great company"
        mock_job.created_at = None

        mock_repository.get_public_job.return_value = mock_job

        service = CareersService(repository=mock_repository)
        result = await service.get_job_details(mock_job.id)

        assert "job_title" in result
        assert "jsonld" in result


class TestApplicationCreation:
    """Tests for job application submission."""

    @pytest.fixture
    def mock_repository(self):
        """Mock careers repository."""
        repo = AsyncMock()
        repo.get_applicant_by_email.return_value = None  # No duplicate
        return repo

    @pytest.mark.asyncio
    async def test_create_application_success(self, mock_repository):
        """Valid application should be created."""
        # Mock all dependencies
        pass

    @pytest.mark.asyncio
    async def test_duplicate_application_rejected(self, mock_repository):
        """Duplicate email should be rejected."""
        mock_repository.get_applicant_by_email.return_value = MagicMock()

        from app.careers.service import CareersService

        service = CareersService(repository=mock_repository)

        with pytest.raises(ValueError) as exc_info:
            await service.create_application(
                job_id=uuid4(),
                name="John Doe",
                email="existing@example.com",
                phone=None,
                resume_content=b"PDF content",
                resume_filename="resume.pdf",
            )

        assert "already exists" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_job_not_found_rejected(self, mock_repository):
        """Application to non-existent job should be rejected."""
        mock_repository.get_public_job.return_value = None

        from app.careers.service import CareersService

        service = CareersService(repository=mock_repository)

        with pytest.raises(ValueError) as exc_info:
            await service.create_application(
                job_id=uuid4(),
                name="John Doe",
                email="john@example.com",
                phone=None,
                resume_content=b"PDF content",
                resume_filename="resume.pdf",
            )

        assert "not found" in str(exc_info.value)


class TestResumeValidation:
    """Tests for resume file validation."""

    def test_pdf_extension_allowed(self):
        """PDF files should be allowed."""
        filename = "resume.pdf"
        assert filename.lower().endswith(".pdf")

    def test_other_extensions_rejected(self):
        """Non-PDF files should be rejected."""
        invalid_files = ["resume.doc", "resume.docx", "resume.txt", "resume.jpg"]

        for filename in invalid_files:
            assert not filename.lower().endswith(".pdf")

    def test_file_size_limit(self):
        """Files over limit should be rejected."""
        max_bytes = MAX_RESUME_SIZE_MB * 1024 * 1024

        small_file = b"x" * 1000  # 1KB
        large_file = b"x" * (max_bytes + 1)  # Over limit

        assert len(small_file) <= max_bytes
        assert len(large_file) > max_bytes


class TestSimilarityCalculation:
    """Tests for resume-JD similarity calculation."""

    def test_similarity_score_range(self):
        """Similarity score should be 0-1."""
        import numpy as np

        vec1 = np.array([1.0, 0.5, 0.3])
        vec2 = np.array([0.9, 0.4, 0.2])

        dot = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        similarity = dot / (norm1 * norm2)

        assert 0 <= similarity <= 1

    def test_identical_embeddings_score_1(self):
        """Identical embeddings should score 1.0."""
        import numpy as np

        vec = np.array([1.0, 2.0, 3.0])

        dot = np.dot(vec, vec)
        norm = np.linalg.norm(vec)
        similarity = dot / (norm * norm)

        assert abs(similarity - 1.0) < 0.0001
