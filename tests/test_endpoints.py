"""
Comprehensive API Endpoint Tests

Tests all AARLP API endpoints to verify they respond correctly.
Uses dependency overrides for auth where needed.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.auth.jwt_dependencies import get_current_user
from app.auth.models import User
from app.jobs.schemas import JobInput


# ============================================================================
# Auth Mock Fixture
# ============================================================================


@pytest.fixture
def mock_user():
    """Create a mock authenticated user."""
    user = MagicMock(spec=User)
    user.id = uuid4()
    user.email = "test@example.com"
    user.is_active = True
    user.is_verified = True
    user.is_superuser = False
    return user


@pytest.fixture
def auth_client(mock_user):
    """TestClient with auth override - all job/candidate endpoints authenticated."""
    async def override_get_current_user():
        return mock_user

    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def client():
    """TestClient without auth - for public endpoints."""
    with TestClient(app) as c:
        yield c


# ============================================================================
# Sample Data
# ============================================================================


@pytest.fixture
def sample_job_input() -> dict:
    """Valid job input for create endpoint."""
    return {
        "role_title": "Senior Backend Engineer",
        "department": "Engineering",
        "company_name": "TechCorp Inc.",
        "company_description": "A leading technology company",
        "key_requirements": ["Python", "FastAPI", "PostgreSQL", "Docker"],
        "nice_to_have": ["Kubernetes", "AWS", "GraphQL"],
        "experience_years": 5,
        "location": "Remote",
        "salary_range": "$150,000 - $200,000",
        "prescreening_questions": [
            "Tell me about your experience with Python (at least 10 chars).",
            "Describe a challenging bug you fixed successfully.",
        ],
    }


# ============================================================================
# Health Endpoints (No Auth)
# ============================================================================


class TestHealthEndpoints:
    """Health check endpoints."""

    def test_root_returns_html(self, client: TestClient):
        """GET / returns HTML landing page."""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers.get("content-type", "")
        assert "AARLP" in response.text

    def test_health_check(self, client: TestClient):
        """GET /health returns status (200 or 503 if DB down)."""
        response = client.get("/health")
        assert response.status_code in (
            status.HTTP_200_OK,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )
        data = response.json()
        assert "status" in data
        assert "checks" in data

    def test_readiness(self, client: TestClient):
        """GET /health/readiness returns ready status."""
        response = client.get("/health/readiness")
        assert response.status_code in (
            status.HTTP_200_OK,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )
        data = response.json()
        assert "status" in data

    def test_liveness(self, client: TestClient):
        """GET /health/liveness always returns 200."""
        response = client.get("/health/liveness")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "alive"


# ============================================================================
# Public Careers Endpoints (No Auth)
# ============================================================================


@pytest.mark.integration
class TestCareersEndpoints:
    """Public careers endpoints - require DB."""

    def test_list_public_jobs(self, client: TestClient):
        """GET /careers/ returns job list."""
        response = client.get("/careers/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "jobs" in data
        assert "total" in data

    def test_job_feed_xml(self, client: TestClient):
        """GET /careers/feed returns XML."""
        response = client.get("/careers/feed")
        assert response.status_code == status.HTTP_200_OK
        assert "application/xml" in response.headers.get("content-type", "")


# ============================================================================
# Auth Endpoints (No Auth for these - we're testing the endpoints exist)
# ============================================================================


class TestAuthEndpoints:
    """Auth endpoints - verify they exist and respond."""

    def test_register_validation(self, client: TestClient):
        """POST /auth/register with invalid data returns 422."""
        response = client.post("/auth/register", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_validation(self, client: TestClient):
        """POST /auth/login with invalid data returns 422."""
        response = client.post("/auth/login", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_verify_otp_validation(self, client: TestClient):
        """POST /auth/verify-otp with invalid data returns 422."""
        response = client.post("/auth/verify-otp", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ============================================================================
# Jobs Endpoints (Require Auth)
# ============================================================================


class TestJobsEndpoints:
    """Job endpoints with auth."""

    def test_list_jobs_requires_auth(self, client: TestClient):
        """GET /jobs/ without auth returns 401."""
        response = client.get("/jobs/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_job_validation_error(self, auth_client: TestClient):
        """POST /jobs/create with invalid data returns 422."""
        response = auth_client.post("/jobs/create", json={"invalid": "data"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.integration
class TestJobsEndpointsIntegration:
    """Job endpoints requiring DB - run with: pytest -m integration."""

    def test_list_jobs_with_auth(self, auth_client: TestClient):
        """GET /jobs/ with auth returns job list."""
        response = auth_client.get("/jobs/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "jobs" in data
        assert "total" in data

    def test_create_job(
        self,
        auth_client: TestClient,
        sample_job_input: dict,
    ):
        """POST /jobs/create creates job and returns job_id."""
        response = auth_client.post("/jobs/create", json=sample_job_input)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "job_id" in data
        assert data["current_node"] == "generate_jd"
        job_id = data["job_id"]

        status_resp = auth_client.get(f"/jobs/status/{job_id}")
        assert status_resp.status_code == status.HTTP_200_OK
        assert status_resp.json()["job_id"] == job_id

    def test_get_job_status_not_found(self, auth_client: TestClient):
        """GET /jobs/status/{id} for non-existent returns 404."""
        response = auth_client.get(
            "/jobs/status/00000000-0000-0000-0000-000000000000"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_job_not_found(self, auth_client: TestClient):
        """DELETE /jobs/{id} for non-existent returns 404."""
        response = auth_client.delete(
            "/jobs/00000000-0000-0000-0000-000000000000"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# Middleware
# ============================================================================


class TestMiddleware:
    """Request/response middleware."""

    def test_correlation_id_in_response(self, client: TestClient):
        """X-Correlation-ID header is present in response."""
        response = client.get("/health/liveness")
        assert "X-Correlation-ID" in response.headers

    def test_custom_correlation_id_preserved(self, client: TestClient):
        """Custom X-Correlation-ID is preserved."""
        custom_id = "test-correlation-123"
        response = client.get(
            "/health/liveness",
            headers={"X-Correlation-ID": custom_id},
        )
        assert response.headers.get("X-Correlation-ID") == custom_id


# ============================================================================
# Docs
# ============================================================================


class TestDocsEndpoints:
    """API documentation endpoints."""

    def test_swagger_ui(self, client: TestClient):
        """GET /docs returns Swagger UI."""
        response = client.get("/docs")
        assert response.status_code == status.HTTP_200_OK

    def test_redoc(self, client: TestClient):
        """GET /redoc returns ReDoc."""
        response = client.get("/redoc")
        assert response.status_code == status.HTTP_200_OK
