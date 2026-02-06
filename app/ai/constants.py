"""
AI Module Constants

Centralized configuration values for AI operations.
"""


# AWS Bedrock Nova Models
class NovaModels:
    """AWS Bedrock Nova model identifiers."""

    LITE = "amazon.nova-lite-v1:0"
    PRO = "amazon.nova-pro-v1:0"
    MICRO = "amazon.nova-micro-v1:0"


# AWS Titan Embedding
class TitanEmbedding:
    """AWS Titan embedding configuration."""

    MODEL_ID = "amazon.titan-embed-text-v2:0"
    DIMENSION = 1024


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
