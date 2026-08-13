"""
Container Settings API for Piwik PRO.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...client import PiwikProClient

from .models import ContainerSettingsListResponse, InstallationCodeResponse


class ContainerSettingsAPI:
    """Container Settings API client for Piwik PRO."""

    def __init__(self, client: "PiwikProClient"):
        """
        Initialize Container Settings API client.

        Args:
            client: Piwik PRO HTTP client instance
        """
        self.client = client

    def get_installation_code(self, app_id: str) -> InstallationCodeResponse:
        """
        Get installation code for an app.

        Args:
            app_id: App UUID

        Returns:
            InstallationCodeResponse: Pydantic model with installation code resource

        Raises:
            NotFoundError: If app is not found
            PiwikProAPIError: If the request fails
        """
        response = self.client.get(f"/api/container-settings/v1/app/{app_id}/installation-code")
        return InstallationCodeResponse(**(response or {}))

    def get_app_settings(self, app_id: str) -> ContainerSettingsListResponse:
        """
        Get container settings for an app.

        Args:
            app_id: App UUID

        Returns:
            ContainerSettingsListResponse: Pydantic model with settings list and meta

        Raises:
            NotFoundError: If app is not found
            PiwikProAPIError: If the request fails
        """
        response = self.client.get(f"/api/container-settings/v1/app/{app_id}/settings")
        return ContainerSettingsListResponse(**(response or {}))

    def update_app_settings(self, app_id: str, settings: list[dict[str, Any]]) -> None:
        """
        Modify one or more of an app's container settings.

        Args:
            app_id: App UUID
            settings: List of JSON:API setting resources, each shaped as
                ``{"id": <setting_name>, "type": "container/app/setting",
                "attributes": {"value": <value>}}``

        Returns:
            None (API returns 204 No Content)

        Raises:
            NotFoundError: If app is not found
            BadRequestError: If request data is invalid
            PiwikProAPIError: If the request fails
        """
        data = {"data": settings}
        self.client.patch(f"/api/container-settings/v1/app/{app_id}/settings", data=data)

    def delete_app_setting(self, app_id: str, setting_name: str) -> None:
        """
        Remove an app's container setting, reverting it to the organization/default value.

        Args:
            app_id: App UUID
            setting_name: Name of the container setting to remove

        Returns:
            None (API returns 204 No Content)

        Raises:
            NotFoundError: If app or setting is not found
            PiwikProAPIError: If the request fails
        """
        self.client.delete(f"/api/container-settings/v1/app/{app_id}/settings/{setting_name}")
