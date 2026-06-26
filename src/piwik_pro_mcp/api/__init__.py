"""
Piwik PRO API Client

A Python client library for interacting with Piwik PRO APIs.
"""

from piwik_pro_mcp._version import __version__

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
    "__version__",
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
