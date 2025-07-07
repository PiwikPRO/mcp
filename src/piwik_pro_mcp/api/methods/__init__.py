"""
Piwik PRO API modules.
"""

from .apps.api import AppsAPI
from .cdp.api import CdpAPI
from .common import ErrorDetail, ErrorResponse, JsonApiData, JsonApiResource, Meta
from .tag_manager.api import TagManagerAPI

__all__ = [
    "AppsAPI",
    "CdpAPI",
    "TagManagerAPI",
    "JsonApiResource",
    "JsonApiData",
    "Meta",
    "ErrorDetail",
    "ErrorResponse",
]
