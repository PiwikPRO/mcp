"""
Container Settings API for Piwik PRO.
"""

from typing import TYPE_CHECKING

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
