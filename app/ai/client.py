"""
AARLP AI Client

Centralized OpenAI client factory.
Avoids creating multiple client instances across the codebase.
"""

from functools import lru_cache

from openai import AsyncOpenAI

from app.core.config import get_settings


@lru_cache(maxsize=1)
def get_openai_client() -> AsyncOpenAI:
    """
    Get cached OpenAI async client.
    
    Uses lru_cache to ensure only one client instance exists.
    """
    settings = get_settings()
    return AsyncOpenAI(api_key=settings.openai_api_key)
