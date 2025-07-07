"""
Customer Data Platform (CDP) API for Piwik PRO.
"""

from .api import CdpAPI
from .models import (
    AudienceAuthor,
    AudienceCondition,
    AudienceDefinition,
    AudienceDetail,
    AudienceListItem,
    AudienceListResponse,
    AudienceResponse,
    ConditionFilter,
    EventCondition,
    EventTimes,
    NewAudienceAttributes,
    ProfileCondition,
)

__all__ = [
    "CdpAPI",
    "AudienceAuthor",
    "AudienceCondition",
    "AudienceDefinition",
    "AudienceDetail",
    "AudienceListItem",
    "AudienceListResponse",
    "AudienceResponse",
    "ConditionFilter",
    "EventCondition",
    "EventTimes",
    "NewAudienceAttributes",
    "ProfileCondition",
]
