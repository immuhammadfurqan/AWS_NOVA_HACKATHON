"""
Core Config Tests

Unit tests for application configuration.
"""

import pytest
from unittest.mock import patch
import os


class TestSettings:
    """Tests for Settings configuration."""

    def test_settings_loads_from_env(self):
        """Settings should load values from environment."""
        from app.core.config import get_settings

        settings = get_settings()

        assert settings.app_name == "AARLP"
        assert isinstance(settings.debug, bool)

    def test_settings_has_database_url(self):
        """Settings should have database URL."""
        from app.core.config import get_settings

        settings = get_settings()

        assert settings.database_url is not None
        assert "postgresql" in settings.database_url

    def test_settings_cached(self):
        """Settings should be cached (same instance)."""
        from app.core.config import get_settings

        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2

    def test_cors_origins_list(self):
        """CORS origins should be parseable to list."""
        from app.core.config import get_settings

        settings = get_settings()
        origins = settings.cors_origins_list

        assert isinstance(origins, list)
        assert len(origins) > 0

    def test_ai_provider_valid_values(self):
        """AI provider should be valid enum value."""
        from app.core.config import get_settings

        settings = get_settings()

        assert settings.ai_provider in ["openai", "bedrock"]

    def test_secret_key_required(self):
        """Secret key must be set."""
        from app.core.config import get_settings

        settings = get_settings()

        assert settings.secret_key is not None
        assert len(settings.secret_key) > 0


class TestDatabaseConfig:
    """Tests for database configuration."""

    def test_database_url_format(self):
        """Database URL should be in correct format."""
        from app.core.config import get_settings

        settings = get_settings()
        url = settings.database_url

        assert url.startswith("postgresql+asyncpg://")


class TestAWSConfig:
    """Tests for AWS configuration."""

    def test_bedrock_model_id_format(self):
        """Bedrock model ID should be in AWS format."""
        from app.core.config import get_settings

        settings = get_settings()

        assert (
            "amazon." in settings.bedrock_model_id
            or "nova" in settings.bedrock_model_id
        )

    def test_embedding_dimension_valid(self):
        """Embedding dimension should be valid."""
        from app.core.config import get_settings

        settings = get_settings()

        assert settings.bedrock_embedding_dimension in [256, 512, 1024]
