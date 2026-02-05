"""
AWS Bedrock Utility Functions

Helpers for message formatting, response parsing, and error handling
when working with AWS Nova models via Bedrock.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class BedrockInvocationError(Exception):
    """Raised when a Bedrock model invocation fails."""

    pass


def format_messages_for_bedrock(messages: list[dict]) -> list[dict]:
    """
    Convert OpenAI-style messages to Bedrock/Nova format.

    OpenAI format:
        [{"role": "user", "content": "Hello"}]

    Bedrock Nova format:
        [{"role": "user", "content": [{"text": "Hello"}]}]

    Args:
        messages: List of message dicts with 'role' and 'content' keys

    Returns:
        List of messages in Bedrock Nova format
    """
    bedrock_messages = []

    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")

        # Skip system messages - they go in a separate field
        if role == "system":
            continue

        # Map 'assistant' to 'assistant' (same in Nova)
        # Map 'user' to 'user' (same in Nova)

        # Handle string content (convert to content block format)
        if isinstance(content, str):
            bedrock_content = [{"text": content}]
        elif isinstance(content, list):
            # Already in content block format, validate structure
            bedrock_content = []
            for item in content:
                if isinstance(item, dict):
                    if "text" in item:
                        bedrock_content.append({"text": item["text"]})
                    elif "image_url" in item:
                        # Handle image content for multimodal
                        bedrock_content.append(item)
                    else:
                        bedrock_content.append({"text": str(item)})
                else:
                    bedrock_content.append({"text": str(item)})
        else:
            bedrock_content = [{"text": str(content)}]

        bedrock_messages.append(
            {
                "role": role,
                "content": bedrock_content,
            }
        )

    return bedrock_messages


def extract_system_prompt(messages: list[dict]) -> str | None:
    """
    Extract system prompt from OpenAI-style messages.

    Args:
        messages: List of message dicts

    Returns:
        System prompt content if found, None otherwise
    """
    for msg in messages:
        if msg.get("role") == "system":
            content = msg.get("content", "")
            if isinstance(content, list):
                # Extract text from content blocks
                texts = [
                    item.get("text", "") for item in content if isinstance(item, dict)
                ]
                return " ".join(texts)
            return content
    return None


def parse_bedrock_response(response: dict) -> str:
    """
    Extract generated text from Bedrock Nova model response.

    Args:
        response: Raw response dict from Bedrock invoke_model

    Returns:
        Generated text content

    Raises:
        BedrockInvocationError: If response format is unexpected
    """
    try:
        # Nova response format
        output = response.get("output", {})
        message = output.get("message", {})
        content = message.get("content", [])

        if not content:
            # Fallback: try direct content access
            content = response.get("content", [])

        if not content:
            logger.warning(f"Empty content in Bedrock response: {response}")
            return ""

        # Extract text from content blocks
        texts = []
        for block in content:
            if isinstance(block, dict) and "text" in block:
                texts.append(block["text"])

        return "".join(texts)

    except Exception as e:
        logger.error(f"Failed to parse Bedrock response: {e}")
        raise BedrockInvocationError(f"Failed to parse response: {e}")


def parse_bedrock_json_response(response: dict) -> dict[str, Any]:
    """
    Parse Bedrock response and extract JSON content.

    Useful for structured outputs like JD generation.

    Args:
        response: Raw response dict from Bedrock invoke_model

    Returns:
        Parsed JSON object from the response

    Raises:
        BedrockInvocationError: If JSON parsing fails
    """
    import json

    text = parse_bedrock_response(response)

    # Try to extract JSON from the response
    # Sometimes models wrap JSON in markdown code blocks
    if "```json" in text:
        start = text.find("```json") + 7
        end = text.find("```", start)
        if end > start:
            text = text[start:end].strip()
    elif "```" in text:
        start = text.find("```") + 3
        end = text.find("```", start)
        if end > start:
            text = text[start:end].strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from response: {e}")
        logger.debug(f"Raw text: {text[:500]}")
        raise BedrockInvocationError(f"Failed to parse JSON response: {e}")


def estimate_token_count(text: str) -> int:
    """
    Rough token count estimation for Nova models.

    Note: This is an approximation. For accurate counts,
    use the model's tokenizer.

    Args:
        text: Input text

    Returns:
        Estimated token count
    """
    # Rough estimate: ~4 characters per token for English text
    return len(text) // 4


def truncate_to_token_limit(text: str, max_tokens: int = 4000) -> str:
    """
    Truncate text to fit within token limit.

    Args:
        text: Input text
        max_tokens: Maximum tokens allowed

    Returns:
        Truncated text
    """
    estimated_chars = max_tokens * 4
    if len(text) > estimated_chars:
        logger.warning(f"Truncating text from {len(text)} to {estimated_chars} chars")
        return text[:estimated_chars]
    return text
