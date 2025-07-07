"""
Piwik PRO Tracker Settings API module.
"""

from .api import TrackerSettingsAPI
from .models import (
    AppTrackerSettings,
    GeolocationLevel,
    GlobalTrackerSettings,
    SessionLimitAction,
)

__all__ = [
    "TrackerSettingsAPI",
    "GlobalTrackerSettings",
    "AppTrackerSettings",
    "GeolocationLevel",
    "SessionLimitAction",
]
