"""
AARLP API Endpoint Tests

Tests for FastAPI endpoints.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.jobs.schemas import JobInput


class TestHealthEndpoints:
    """Tests for health check endpoints."""
    
    def test_root_endpoint(self, client: TestClient):
        """Test root health check returns healthy."""
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "AARLP"
    
    def test_health_endpoint(self, client: TestClient):
        """Test detailed health check."""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"


class TestJobEndpoints:
    """Tests for job-related endpoints."""
    
    def test_create_job_success(
        self,
        client: TestClient,
        sample_job_input: JobInput,
    ):
        """Test creating a new job succeeds."""
        response = client.post(
            "/jobs/create",
            json=sample_job_input.model_dump(),
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "job_id" in data
        assert data["current_node"] == "generate_jd"
    
    def test_create_job_validation_error(self, client: TestClient):
        """Test creating job with invalid data fails."""
        response = client.post(
            "/jobs/create",
            json={"invalid": "data"},
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_job_status_not_found(self, client: TestClient):
        """Test getting status for non-existent job."""
        response = client.get("/jobs/status/non-existent-id")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_job_status_success(
        self,
        client: TestClient,
        sample_job_input: JobInput,
    ):
        """Test getting status for existing job."""
        # First create a job
        create_response = client.post(
            "/jobs/create",
            json=sample_job_input.model_dump(),
        )
        job_id = create_response.json()["job_id"]
        
        # Then get its status
        response = client.get(f"/jobs/status/{job_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["job_id"] == job_id


class TestCandidateEndpoints:
    """Tests for candidate-related endpoints."""
    
    def test_get_applicants_not_found(self, client: TestClient):
        """Test getting applicants for non-existent job."""
        response = client.get("/jobs/non-existent/applicants")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_reject_candidate_not_found(self, client: TestClient):
        """Test rejecting candidate for non-existent job."""
        response = client.post("/jobs/non-existent/candidates/abc/reject")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCorrelationId:
    """Tests for correlation ID middleware."""
    
    def test_correlation_id_in_response(self, client: TestClient):
        """Test that correlation ID is returned in response."""
        response = client.get("/")
        
        assert "X-Correlation-ID" in response.headers
    
    def test_custom_correlation_id_preserved(self, client: TestClient):
        """Test that custom correlation ID is preserved."""
        custom_id = "test-correlation-123"
        response = client.get(
            "/",
            headers={"X-Correlation-ID": custom_id},
        )
        
        assert response.headers["X-Correlation-ID"] == custom_id
