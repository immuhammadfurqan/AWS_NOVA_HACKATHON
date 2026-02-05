"""
AWS Bedrock Client Factory

Centralized client for Amazon Bedrock foundation models (AWS Nova).
Mirrors the pattern used in client.py for OpenAI.

Clean Code Principles Applied:
- Single Responsibility: Each function has one clear purpose
- Dependency Inversion: Uses config for all settings, no hardcoded values
- Consistent error handling pattern
"""

import json
from contextlib import asynccontextmanager
from enum import Enum
from functools import lru_cache
from typing import Any, AsyncGenerator, Optional

import aioboto3
import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class NovaModelId(str, Enum):
    """AWS Nova model identifiers for Amazon Bedrock."""

    # Text generation models
    NOVA_LITE = "amazon.nova-lite-v1:0"
    NOVA_PRO = "amazon.nova-pro-v1:0"
    NOVA_PREMIER = "amazon.nova-premier-v1:0"

    # Multimodal embedding
    NOVA_EMBED_TEXT = "amazon.titan-embed-text-v2:0"
    NOVA_EMBED_MULTIMODAL = "amazon.titan-embed-image-v1:0"

    # Voice / Sonic (for future Voice AI category)
    NOVA_SONIC = "amazon.nova-sonic-v1:0"


# Retry configuration for Bedrock API calls
BEDROCK_RETRY_CONFIG = BotoConfig(
    retries={
        "max_attempts": 3,
        "mode": "adaptive",
    },
    read_timeout=60,
    connect_timeout=10,
)


@lru_cache(maxsize=1)
def get_bedrock_client() -> boto3.client:
    """
    Get cached synchronous Bedrock runtime client.

    Uses lru_cache to ensure only one client instance exists.
    For async operations, use get_async_bedrock_client() instead.
    """
    settings = get_settings()

    return boto3.client(
        "bedrock-runtime",
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region,
        config=BEDROCK_RETRY_CONFIG,
    )


@lru_cache(maxsize=1)
def get_aioboto3_session() -> aioboto3.Session:
    """Get cached aioboto3 session for async Bedrock operations."""
    return aioboto3.Session()


@asynccontextmanager
async def get_async_bedrock_client() -> AsyncGenerator[Any, None]:
    """
    Get async Bedrock runtime client as context manager.

    Usage:
        async with get_async_bedrock_client() as client:
            response = await client.invoke_model(...)
    """
    settings = get_settings()
    session = get_aioboto3_session()

    async with session.client(
        "bedrock-runtime",
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region,
        config=BEDROCK_RETRY_CONFIG,
    ) as client:
        yield client


async def invoke_nova_model(
    messages: list[dict],
    model_id: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: int = 4096,
    system_prompt: Optional[str] = None,
) -> str:
    """
    Invoke an AWS Nova model with the given messages.

    Args:
        messages: List of message dicts with 'role' and 'content' keys
        model_id: Bedrock model ID (defaults to settings.bedrock_model_id)
        temperature: Sampling temperature (defaults to settings.llm_temperature)
        max_tokens: Maximum tokens to generate
        system_prompt: Optional system prompt

    Returns:
        Generated text content from the model

    Raises:
        BedrockInvocationError: If the API call fails
    """
    from app.ai.bedrock_utils import (
        format_messages_for_bedrock,
        parse_bedrock_response,
        BedrockInvocationError,
    )

    settings = get_settings()

    model_id = model_id or settings.bedrock_model_id
    temperature = temperature if temperature is not None else settings.llm_temperature

    # Build the request body for Nova models
    request_body = {
        "messages": format_messages_for_bedrock(messages),
        "inferenceConfig": {
            "maxTokens": max_tokens,
            "temperature": temperature,
        },
    }

    if system_prompt:
        request_body["system"] = [{"text": system_prompt}]

    logger.debug(f"Invoking Bedrock model: {model_id}")

    try:
        async with get_async_bedrock_client() as client:
            response = await client.invoke_model(
                modelId=model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(request_body),
            )

            response_body = await response["body"].read()
            response_json = json.loads(response_body)

            return parse_bedrock_response(response_json)

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_message = e.response.get("Error", {}).get("Message", str(e))
        logger.error(f"Bedrock API error [{error_code}]: {error_message}")
        raise BedrockInvocationError(f"Bedrock invocation failed: {error_message}")
    except Exception as e:
        logger.error(f"Unexpected error invoking Bedrock: {e}")
        raise BedrockInvocationError(f"Unexpected error: {str(e)}")


async def generate_embedding(
    text: str,
    model_id: Optional[str] = None,
) -> list[float]:
    """
    Generate embeddings using AWS Nova/Titan embedding model.

    Args:
        text: Text to embed
        model_id: Embedding model ID (defaults to settings.bedrock_embedding_model_id)

    Returns:
        List of floats representing the embedding vector
    """
    from app.ai.bedrock_utils import BedrockInvocationError

    settings = get_settings()
    model_id = model_id or settings.bedrock_embedding_model_id

    # Titan embedding request format
    # Use configured dimension instead of hardcoded value
    request_body = {
        "inputText": text[: settings.max_embedding_text_length],
        "dimensions": settings.bedrock_embedding_dimension,
        "normalize": True,
    }

    try:
        async with get_async_bedrock_client() as client:
            response = await client.invoke_model(
                modelId=model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(request_body),
            )

            response_body = await response["body"].read()
            response_json = json.loads(response_body)

            return response_json.get("embedding", [])

    except ClientError as e:
        error_message = e.response.get("Error", {}).get("Message", str(e))
        logger.error(f"Bedrock embedding error: {error_message}")
        raise BedrockInvocationError(f"Embedding generation failed: {error_message}")
    except Exception as e:
        logger.error(f"Unexpected error generating embedding: {e}")
        raise BedrockInvocationError(f"Unexpected error: {str(e)}")


async def test_bedrock_connection() -> bool:
    """
    Test connectivity to AWS Bedrock.

    Returns:
        True if connection is successful, False otherwise
    """
    try:
        async with get_async_bedrock_client() as client:
            # Simple test invoke with minimal tokens
            response = await client.invoke_model(
                modelId=NovaModelId.NOVA_LITE.value,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(
                    {
                        "messages": [{"role": "user", "content": [{"text": "Hi"}]}],
                        "inferenceConfig": {"maxTokens": 10},
                    }
                ),
            )
            logger.info("Bedrock connection test successful")
            return True
    except Exception as e:
        logger.error(f"Bedrock connection test failed: {e}")
        return False
