"""
AI Module Constants

Centralized configuration values for AI operations.
"""


# AWS Bedrock Nova 2 Models
class NovaModels:
    """AWS Bedrock Nova 2 model identifiers."""

    LITE = "global.amazon.nova-2-lite-v1:0"
    MULTIMODAL_EMBEDDINGS = "amazon.nova-2-multimodal-embeddings-v1:0"
    SONIC = "amazon.nova-2-sonic-v1:0"


# OpenAI Models (Fallback)
class OpenAIModels:
    """OpenAI model identifiers for fallback."""

    GPT4 = "gpt-4o"
    GPT35 = "gpt-3.5-turbo"
    EMBEDDING = "text-embedding-3-small"
    EMBEDDING_DIMENSION = 1536


# Generation Settings
class GenerationSettings:
    """AI text generation settings."""

    DEFAULT_TEMPERATURE = 0.7
    MAX_TOKENS_JD = 4000
    MAX_TOKENS_FEEDBACK = 2000
    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 1


class EmbeddingLimits:
    """OpenAI embedding generation limits."""

    MAX_TEXT_LENGTH = 8000  # OpenAI input limit
    VECTOR_DIMENSION = 1536  # text-embedding-3-small
    BATCH_SIZE = 100
    MIN_SCORE_THRESHOLD = 0.5


class VoiceCallSettings:
    """Voice call configuration."""

    CALL_COMPLETION_WAIT_SECONDS = 2
    MAX_RESPONSE_DURATION_SECONDS = 120
    PAUSE_BETWEEN_QUESTIONS_SECONDS = 1
    DEFAULT_VOICE = "Polly.Joanna"


class PDFParsingSettings:
    """PDF parsing limits."""

    MAX_LINE_LENGTH = 500
    MAX_TOTAL_LENGTH = 50000
