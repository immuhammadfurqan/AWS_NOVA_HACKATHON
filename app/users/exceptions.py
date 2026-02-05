"""
User Exceptions
"""

from app.core.exceptions import AARLPException


class UserError(AARLPException):
    """Base exception for user-related errors."""

    pass
