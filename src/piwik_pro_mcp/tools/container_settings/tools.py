"""
Container Settings MCP tools.

Provides tools for fetching installation code and app container settings.
"""

from mcp.server.fastmcp import FastMCP

from piwik_pro_mcp.api.methods.container_settings.models import ContainerSettingsListResponse

from ...common.utils import create_piwik_client
from ...responses import InstallationCodeMCPResponse


def get_installation_code(app_id: str) -> InstallationCodeMCPResponse:
    try:
        client = create_piwik_client()
        response = client.container_settings.get_installation_code(app_id)
        return InstallationCodeMCPResponse(code=response.data.attributes["code"])
    except Exception as e:
        raise RuntimeError(f"Failed to get installation code: {str(e)}")


def get_container_settings(app_id: str) -> ContainerSettingsListResponse:
    try:
        client = create_piwik_client()
        return client.container_settings.get_app_settings(app_id)
    except Exception as e:
        raise RuntimeError(f"Failed to get container settings: {str(e)}")


def register_container_settings_tools(mcp: FastMCP) -> None:
    """
    Register container settings tools with the MCP server.
    """

    @mcp.tool(annotations={"title": "Piwik PRO: Get Installation Code", "readOnlyHint": True})
    def container_settings_get_installation_code(app_id: str) -> InstallationCodeMCPResponse:
        """
        Get installation code for an app.

        Args:
            app_id: UUID of the app

        Returns:
            Object with a single field:
            - code: Installation code string

        Examples:
            container_settings_get_installation_code(app_id="00000000-0000-4000-8000-000000000000")
        """
        return get_installation_code(app_id)

    @mcp.tool(annotations={"title": "Piwik PRO: List Container Settings", "readOnlyHint": True})
    def container_settings_list(app_id: str) -> ContainerSettingsListResponse:
        """
        Get container settings for an app.

        Args:
            app_id: UUID of the app

        Returns:
            JSON:API response with settings list in 'data' and pagination in 'meta'.

        Examples:
            container_settings_list(app_id="00000000-0000-4000-8000-000000000000")
        """
        return get_container_settings(app_id)
