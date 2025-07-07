"""
Tracker Settings API for Piwik PRO.
"""

from typing import TYPE_CHECKING, Any, Dict, Union

if TYPE_CHECKING:
    from ...client import PiwikProClient
from .models import AppTrackerSettings, GlobalTrackerSettings


class TrackerSettingsAPI:
    """Tracker Settings API client for Piwik PRO."""

    def __init__(self, client: "PiwikProClient"):
        """
        Initialize Tracker Settings API client.

        Args:
            client: Piwik PRO HTTP client instance
        """
        self.client = client

    # Global Settings API

    def get_global_settings(self) -> Union[Dict[str, Any], None]:
        """
        Get global tracker settings.

        Returns:
            Dictionary containing global tracker settings

        Raises:
            PiwikProAPIError: If the request fails
        """
        return self.client.get("/api/tracker/v1/settings/app/global")

    def update_global_settings(self, **kwargs) -> None:
        """
        Update global tracker settings.

        Args:
            **kwargs: Global tracker settings attributes (see GlobalTrackerSettings)

        Returns:
            None (204 No Content)

        Raises:
            BadRequestError: If request data is invalid
            PiwikProAPIError: If the request fails
        """
        attributes = GlobalTrackerSettings(**kwargs)

        data = {
            "data": {
                "type": "tracker/settings/app/global",
                "id": "global",
                "attributes": attributes.model_dump(by_alias=True, exclude_none=True),
            }
        }

        self.client.patch("/api/tracker/v1/settings/app/global", data=data)

    # App Settings API

    def get_app_settings(self, app_id: str) -> Union[Dict[str, Any], None]:
        """
        Get tracker settings for a specific app.

        Args:
            app_id: UUID of the app

        Returns:
            Dictionary containing app tracker settings

        Raises:
            NotFoundError: If app is not found
            PiwikProAPIError: If the request fails
        """
        return self.client.get(f"/api/tracker/v2/settings/app/{app_id}")

    def update_app_settings(self, app_id: str, **kwargs) -> None:
        """
        Update tracker settings for a specific app.

        Args:
            app_id: UUID of the app
            **kwargs: App tracker settings attributes (see AppTrackerSettings)

        Returns:
            None (204 No Content)

        Raises:
            NotFoundError: If app is not found
            BadRequestError: If request data is invalid
            PiwikProAPIError: If the request fails
        """
        attributes = AppTrackerSettings(**kwargs)

        data = {
            "data": {
                "type": "tracker/settings/app",
                "id": app_id,
                "attributes": attributes.model_dump(by_alias=True, exclude_none=True),
            }
        }

        self.client.patch(f"/api/tracker/v2/settings/app/{app_id}", data=data)

    def delete_app_setting(self, app_id: str, setting: str) -> None:
        """
        Delete a specific tracker setting for an app.

        This causes the setting to revert to the global setting.

        Args:
            app_id: UUID of the app
            setting: Name of the tracker setting to delete

        Returns:
            None (204 No Content)

        Raises:
            NotFoundError: If app or setting is not found
            PiwikProAPIError: If the request fails
        """
        self.client.delete(f"/api/tracker/v2/settings/app/{app_id}/{setting}")
