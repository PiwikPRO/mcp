"""
Custom exceptions for Piwik PRO API client.
"""

from typing import Any, Dict, Optional


class PiwikProAPIError(Exception):
    """Base exception for Piwik PRO API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(self.message)


class AuthenticationError(PiwikProAPIError):
    """Raised when authentication fails."""

    pass


class NotFoundError(PiwikProAPIError):
    """Raised when a resource is not found."""

    pass


class BadRequestError(PiwikProAPIError):
    """Raised when the request is malformed."""

    pass


class ConflictError(PiwikProAPIError):
    """Raised when there's a conflict with the current state."""

    pass


class ForbiddenError(PiwikProAPIError):
    """Raised when access is forbidden."""

    pass
