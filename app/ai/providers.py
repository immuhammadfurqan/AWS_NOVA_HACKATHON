"""
AI Provider Abstraction Layer

Implements the Strategy Pattern for AI providers, enabling clean switching
between OpenAI and AWS Bedrock without modifying business logic.

Clean Code Principles:
- Open/Closed Principle: New providers can be added without modifying existing code
- Dependency Inversion: High-level modules depend on abstractions, not implementations
- Strategy Pattern: Encapsulates provider-specific algorithms
"""

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

from app.core.config import get_settings
from app.core.logging import get_logger
from app.ai.client import is_bedrock_provider

logger = get_logger(__name__)


@runtime_checkable
class TextGenerator(Protocol):
    """Protocol for text generation providers."""

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 4096,
        temperature: float | None = None,
    ) -> str:
        """Generate text from prompt."""
        ...


@runtime_checkable
class EmbeddingGenerator(Protocol):
    """Protocol for embedding generation providers."""

    async def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding vector for text."""
        ...


class OpenAIProvider:
    """OpenAI implementation of AI provider protocols."""

    def __init__(self):
        from app.ai.client import get_openai_client

        self._client = get_openai_client()
        self._settings = get_settings()

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 4096,
        temperature: float | None = None,
    ) -> str:
        """Generate text using OpenAI GPT."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self._client.chat.completions.create(
            model=self._settings.openai_model,
            messages=messages,
            temperature=temperature or self._settings.llm_temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content

    async def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding using OpenAI."""
        response = await self._client.embeddings.create(
            model=self._settings.openai_embedding_model,
            input=text,
        )
        return response.data[0].embedding


class BedrockProvider:
    """AWS Bedrock implementation of AI provider protocols."""

    def __init__(self):
        self._settings = get_settings()

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 4096,
        temperature: float | None = None,
    ) -> str:
        """Generate text using AWS Nova."""
        from app.ai.bedrock_client import invoke_nova_model

        messages = [{"role": "user", "content": prompt}]

        result = await invoke_nova_model(
            messages=messages,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        # Handle potential JSON markdown wrapping
        return self._extract_json(result)

    async def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding using AWS Titan."""
        from app.ai.bedrock_client import generate_embedding

        return await generate_embedding(text)

    @staticmethod
    def _extract_json(result: str) -> str:
        """Extract JSON from potential markdown code blocks."""
        if "```json" in result:
            start = result.find("```json") + 7
            end = result.find("```", start)
            if end > start:
                return result[start:end].strip()
        elif "```" in result:
            start = result.find("```") + 3
            end = result.find("```", start)
            if end > start:
                return result[start:end].strip()
        return result


def get_ai_provider_instance() -> OpenAIProvider | BedrockProvider:
    """
    Factory function to get the appropriate AI provider instance.

    Returns:
        Provider instance based on AI_PROVIDER config setting
    """
    if is_bedrock_provider():
        logger.debug("Using Bedrock provider")
        return BedrockProvider()
    else:
        logger.debug("Using OpenAI provider")
        return OpenAIProvider()
