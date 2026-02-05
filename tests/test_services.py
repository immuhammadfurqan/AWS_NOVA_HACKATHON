"""
AARLP Service Tests

Tests for service layer business logic.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.config import Settings
from app.models import (
    JobInput,
    GeneratedJD,
    Applicant,
    RecruitmentNodeStatus,
)
from app.services.job_service import JobService
from app.services.embedding_service import EmbeddingService
from app.exceptions import RecordNotFoundError, InvalidStateTransitionError


class TestJobService:
    """Tests for JobService."""
    
    @pytest.fixture
    def job_service(self, test_settings: Settings) -> JobService:
        """Create a JobService instance for testing."""
        return JobService(test_settings)
    
    @pytest.mark.asyncio
    async def test_create_job(
        self,
        job_service: JobService,
        sample_job_input: JobInput,
    ):
        """Test creating a job."""
        response = await job_service.create_job(sample_job_input)
        
        assert response.job_id is not None
        assert response.current_node == RecruitmentNodeStatus.GENERATE_JD
    
    @pytest.mark.asyncio
    async def test_get_job_state_not_found(self, job_service: JobService):
        """Test getting non-existent job raises error."""
        with pytest.raises(RecordNotFoundError):
            await job_service.get_job_state("non-existent")
    
    @pytest.mark.asyncio
    async def test_get_job_state_success(
        self,
        job_service: JobService,
        sample_job_input: JobInput,
    ):
        """Test getting existing job state."""
        # Create a job first
        response = await job_service.create_job(sample_job_input)
        job_id = str(response.job_id)
        
        # Get its state
        state = await job_service.get_job_state(job_id)
        
        assert state["job_id"] == job_id
    
    @pytest.mark.asyncio
    async def test_approve_shortlist_invalid_state(
        self,
        job_service: JobService,
        sample_job_input: JobInput,
    ):
        """Test approving shortlist in wrong state."""
        response = await job_service.create_job(sample_job_input)
        job_id = str(response.job_id)
        
        # Job is in generate_jd state, not shortlist_candidates
        with pytest.raises(InvalidStateTransitionError):
            await job_service.approve_shortlist(job_id)
    
    @pytest.mark.asyncio
    async def test_add_mock_applicants(
        self,
        job_service: JobService,
        sample_job_input: JobInput,
    ):
        """Test adding mock applicants."""
        response = await job_service.create_job(sample_job_input)
        job_id = str(response.job_id)
        
        result = await job_service.add_mock_applicants(job_id, 3)
        
        assert result["total_applicants"] == 3


class TestEmbeddingService:
    """Tests for EmbeddingService."""
    
    @pytest.fixture
    def embedding_service(self, test_settings: Settings) -> EmbeddingService:
        """Create an EmbeddingService instance for testing."""
        return EmbeddingService(test_settings)
    
    def test_calculate_similarity_identical(self, embedding_service: EmbeddingService):
        """Test similarity of identical vectors is 1."""
        import asyncio
        
        vec = [1.0, 0.0, 0.0]
        similarity = asyncio.get_event_loop().run_until_complete(
            embedding_service.calculate_similarity(vec, vec)
        )
        
        assert abs(similarity - 1.0) < 0.0001
    
    def test_calculate_similarity_orthogonal(self, embedding_service: EmbeddingService):
        """Test similarity of orthogonal vectors is 0."""
        import asyncio
        
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 1.0, 0.0]
        similarity = asyncio.get_event_loop().run_until_complete(
            embedding_service.calculate_similarity(vec1, vec2)
        )
        
        assert abs(similarity) < 0.0001
    
    def test_calculate_similarity_zero_vector(self, embedding_service: EmbeddingService):
        """Test similarity with zero vector returns 0."""
        import asyncio
        
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 0.0, 0.0]
        similarity = asyncio.get_event_loop().run_until_complete(
            embedding_service.calculate_similarity(vec1, vec2)
        )
        
        assert similarity == 0.0
    
    @pytest.mark.asyncio
    async def test_rank_candidates_empty_list(
        self,
        embedding_service: EmbeddingService,
        sample_generated_jd: GeneratedJD,
    ):
        """Test ranking empty candidate list."""
        with patch.object(embedding_service, 'generate_embedding', new_callable=AsyncMock) as mock:
            mock.return_value = [0.1] * 1536
            
            result = await embedding_service.rank_candidates(sample_generated_jd, [])
            
            assert result == []


class TestServiceLogging:
    """Tests for service logging functionality."""
    
    def test_service_has_logger(self, test_settings: Settings):
        """Test that services have loggers configured."""
        service = JobService(test_settings)
        
        assert service.logger is not None
        assert service.logger.name == "JobService"
    
    def test_service_has_settings(self, test_settings: Settings):
        """Test that services have settings configured."""
        service = JobService(test_settings)
        
        assert service.settings is not None
        assert service.settings.debug is True
