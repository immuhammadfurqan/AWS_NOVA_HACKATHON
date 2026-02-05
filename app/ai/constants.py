"""
AI Module Constants

Centralized configuration values for AI operations.
"""


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
