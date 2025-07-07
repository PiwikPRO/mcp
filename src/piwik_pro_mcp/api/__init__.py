"""
Piwik PRO API Client

A Python client library for interacting with Piwik PRO APIs.
"""

__version__ = "0.1.0"

from .client import PiwikProClient
from .exceptions import (
    AuthenticationError,
    BadRequestError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    PiwikProAPIError,
)
from .methods.apps import AppsAPI
from .methods.cdp import CdpAPI
from .methods.tracker_settings import TrackerSettingsAPI

__all__ = [
    "PiwikProClient",
    "AppsAPI",
    "CdpAPI",
    "TrackerSettingsAPI",
    "PiwikProAPIError",
    "AuthenticationError",
    "NotFoundError",
    "BadRequestError",
    "ConflictError",
    "ForbiddenError",
]
