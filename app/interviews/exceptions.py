"""
Interview Service Exceptions
"""

from typing import Optional
from app.core.exceptions import ExternalServiceError


class GoogleCalendarError(ExternalServiceError):
    """Raised when Google Calendar API calls fail."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        super().__init__("GoogleCalendar", message, status_code)
        self.error_code = "CALENDAR_ERROR"
