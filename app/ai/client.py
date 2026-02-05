"""
AARLP AI Client

Centralized AI client factory supporting multiple providers:
- OpenAI (legacy/fallback)
- AWS Bedrock with Nova models (primary for hackathon)

Clean Code Principles Applied:
- Open/Closed: New providers can be added without modifying existing code
- Single Responsibility: Each function has one clear purpose
- DRY: Provider selection logic centralized

Provider selection is controlled by AI_PROVIDER env var.
"""

from functools import lru_cache
from typing import Literal

from openai import AsyncOpenAI

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

AIProvider = Literal["openai", "bedrock"]


@lru_cache(maxsize=1)
def get_ai_provider() -> AIProvider:
    """
    Get the configured AI provider.

    Returns:
        "openai" or "bedrock" based on AI_PROVIDER env var
    """
    settings = get_settings()
    provider = settings.ai_provider
    logger.info(f"AI Provider: {provider}")
    return provider


def is_bedrock_provider() -> bool:
    """Check if Bedrock is the active AI provider."""
    return get_ai_provider() == "bedrock"


def is_openai_provider() -> bool:
    """Check if OpenAI is the active AI provider."""
    return get_ai_provider() == "openai"


@lru_cache(maxsize=1)
def get_openai_client() -> AsyncOpenAI:
    """
    Get cached OpenAI async client.

    Uses lru_cache to ensure only one client instance exists.
    Note: For hackathon, prefer Bedrock. Use this for fallback.
    """
    settings = get_settings()

    if is_bedrock_provider():
        logger.warning(
            "OpenAI client requested but AI_PROVIDER=bedrock. "
            "Consider using Bedrock client instead."
        )

    return AsyncOpenAI(api_key=settings.openai_api_key)


def get_embedding_dimension() -> int:
    """
    Get the embedding dimension for the active provider.

    Returns:
        1536 for OpenAI, 1024 for Bedrock/Nova
    """
    settings = get_settings()
    if is_bedrock_provider():
        return settings.bedrock_embedding_dimension
    return settings.openai_embedding_dimension
