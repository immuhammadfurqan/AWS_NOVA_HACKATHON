"""
AARLP API Endpoint Tests (Legacy)

Legacy tests - comprehensive endpoint tests are in test_endpoints.py
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_root_endpoint(self, client: TestClient):
        """Root returns HTML with AARLP."""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        assert "AARLP" in response.text

    def test_health_endpoint(self, client: TestClient):
        """Health returns status (200 or 503 if DB unavailable)."""
        response = client.get("/health")
        assert response.status_code in (
            status.HTTP_200_OK,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )
        data = response.json()
        assert "status" in data


class TestCorrelationId:
    """Tests for correlation ID middleware."""

    def test_correlation_id_in_response(self, client: TestClient):
        """Correlation ID is returned in response headers."""
        response = client.get("/health/liveness")
        assert "X-Correlation-ID" in response.headers

    def test_custom_correlation_id_preserved(self, client: TestClient):
        """Custom correlation ID is preserved."""
        custom_id = "test-correlation-123"
        response = client.get(
            "/health/liveness",
            headers={"X-Correlation-ID": custom_id},
        )
        assert response.headers.get("X-Correlation-ID") == custom_id
