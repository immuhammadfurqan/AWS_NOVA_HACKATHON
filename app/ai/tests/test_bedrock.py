"""
AI Bedrock Client Tests

Unit tests for AWS Bedrock Nova 2 integration.
"""

import pytest
from unittest.mock import patch

from app.ai.constants import NovaModels, GenerationSettings
from app.ai.bedrock_client import NovaModelId


class TestNovaModelsConstants:
    """Tests for Nova 2 model constants."""

    def test_nova_2_lite_model_id(self):
        """Nova 2 Lite model ID should be valid."""
        assert "nova-2-lite" in NovaModels.LITE
        assert "amazon." in NovaModels.LITE

    def test_nova_2_multimodal_embeddings_model_id(self):
        """Nova 2 Multimodal Embeddings model ID should be valid."""
        assert "nova-2-multimodal-embeddings" in NovaModels.MULTIMODAL_EMBEDDINGS

    def test_nova_2_sonic_model_id(self):
        """Nova 2 Sonic model ID should be valid."""
        assert "nova-2-sonic" in NovaModels.SONIC


class TestNovaModelIdEnum:
    """Tests for NovaModelId enum."""

    def test_nova_2_lite(self):
        """Nova 2 Lite should match constants."""
        assert NovaModelId.NOVA_2_LITE.value == NovaModels.LITE

    def test_nova_2_multimodal_embeddings(self):
        """Nova 2 Multimodal Embeddings should match constants."""
        assert NovaModelId.NOVA_2_MULTIMODAL_EMBEDDINGS.value == NovaModels.MULTIMODAL_EMBEDDINGS


class TestGenerationSettings:
    """Tests for generation settings."""

    def test_temperature_range(self):
        """Temperature should be in valid range."""
        assert 0.0 <= GenerationSettings.DEFAULT_TEMPERATURE <= 1.0

    def test_max_tokens_positive(self):
        """Max tokens should be positive."""
        assert GenerationSettings.MAX_TOKENS_JD > 0
        assert GenerationSettings.MAX_TOKENS_FEEDBACK > 0


class TestJDGeneration:
    """Tests for JD generation functionality."""

    def test_jd_response_validation(self):
        """JD response should match expected schema."""
        from app.jobs.schemas import GeneratedJD

        # Mock response data
        jd_data = {
            "job_title": "Software Engineer",
            "summary": "We are looking for...",
            "description": "Full description...",
            "responsibilities": ["Build features", "Code review"],
            "requirements": ["3+ years experience", "Python"],
            "nice_to_have": ["AWS", "Docker"],
            "benefits": ["Health insurance", "401k"],
            "location": "Remote",
            "salary_range": "$100k-$150k",
        }

        # Should validate without error
        jd = GeneratedJD(**jd_data)

        assert jd.job_title == "Software Engineer"
        assert len(jd.responsibilities) == 2
