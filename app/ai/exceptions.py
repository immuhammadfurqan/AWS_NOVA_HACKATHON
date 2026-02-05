"""
AI Service Exceptions
"""

from typing import Optional
from app.core.exceptions import ExternalServiceError


class OpenAIError(ExternalServiceError):
    """Raised when OpenAI API calls fail."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        super().__init__("OpenAI", message, status_code)
        self.error_code = "OPENAI_ERROR"


class TwilioError(ExternalServiceError):
    """Raised when Twilio API calls fail."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        super().__init__("Twilio", message, status_code)
        self.error_code = "TWILIO_ERROR"
