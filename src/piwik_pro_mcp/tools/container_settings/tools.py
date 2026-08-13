"""
Container Settings MCP tools.

Provides tools for fetching installation code and app container settings.
"""

from mcp.server.fastmcp import FastMCP

from piwik_pro_mcp.api.exceptions import BadRequestError, NotFoundError
from piwik_pro_mcp.api.methods.container_settings.models import ContainerSettingsListResponse

from ...common.utils import create_piwik_client, validate_data_against_model
from ...responses import InstallationCodeMCPResponse, OperationStatusResponse, UpdateStatusResponse
from .models import CONTAINER_APP_SETTING_NAMES, ContainerAppSettingsUpdate


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


def update_container_settings(app_id: str, attributes: dict) -> UpdateStatusResponse:
    try:
        client = create_piwik_client()

        validated = validate_data_against_model(attributes, ContainerAppSettingsUpdate)

        updated_fields = [setting.id for setting in validated.data]
        items = [setting.to_jsonapi_item() for setting in validated.data]

        client.container_settings.update_app_settings(app_id, items)

        return UpdateStatusResponse(
            status="success",
            message=f"App {app_id} container settings updated successfully",
            updated_fields=updated_fields,
        )
    except NotFoundError:
        raise RuntimeError(f"App with ID {app_id} not found")
    except BadRequestError as e:
        raise RuntimeError(f"Failed to update container settings: {e.message}")
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to update container settings: {str(e)}")


def delete_container_setting(app_id: str, setting_name: str) -> OperationStatusResponse:
    try:
        if setting_name not in CONTAINER_APP_SETTING_NAMES:
            raise RuntimeError(
                f"Unknown container setting '{setting_name}'. Valid settings: {sorted(CONTAINER_APP_SETTING_NAMES)}"
            )

        client = create_piwik_client()
        client.container_settings.delete_app_setting(app_id, setting_name)

        return OperationStatusResponse(
            status="success",
            message=f"Container setting '{setting_name}' deleted successfully for app {app_id}",
        )
    except NotFoundError:
        raise RuntimeError(f"App with ID {app_id} or setting '{setting_name}' not found")
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to delete container setting: {str(e)}")


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

    @mcp.tool(annotations={"title": "Piwik PRO: Update Container Settings"})
    def container_settings_app_update(app_id: str, attributes: dict) -> UpdateStatusResponse:
        """Change an app's container (tracking container) settings.

        Use this tool to enable, disable, turn on/off, or set any of an app's container
        settings. It covers requests such as "enable automatic scroll tracking", "turn off
        SPA tracking", "enable/disable FPC", and "set the tracking domain /
        static resources domain / UI & APIs domain / container JS path / tracking script path
        / tracking endpoint path". Settings not listed in the request are left unchanged.

        This is the tool for CUSTOMIZING THE DOMAINS AND PATHS used to track and serve a
        Piwik PRO Tag Manager container (ContainerJS). Any request to use a custom / branded /
        first-party domain, a CDN or self-hosted host, or a custom URL path for the container
        script, the tracker, or the tracking (collection) endpoint routes here. The
        container's domain-like / serving settings are:
        - "fpc" (First Party Collector) — serve tracking from a first-party collector
        - "tracking_domain", "static_resources_domain", "ui_apis_domain" — the hostnames the
          container uses to track and to load its resources & UI/APIs
        - "container_js_path", "tracking_script_path", "tracking_endpoint_path" — the URL
          paths for the ContainerJS, the tracking script, and the tracking (collection) endpoint

        About "fpc" and how it gates domains/paths:
        "fpc" is a flag indicating whether the user runs their own infrastructure (e.g. a reverse
        proxy pointing to the Piwik PRO backend) and therefore serves the container from domains
        that are NOT registered in the product (the Domains API).
        - When fpc is ENABLED: the user may set the domain and path settings to arbitrary custom
          values, including hostnames that are not configured in the product.
        - When fpc is DISABLED: only domains previously added to the product (via the Domains API)
          are valid; custom/unregistered hostnames are not allowed.
        So a request to use a custom, unregistered domain typically means enabling "fpc" as well
        as setting the domain/path settings.

        Supported settings and their value shape:
        - On/off toggles (value is {"is_enabled": true|false}):
            - "spa_tracking" (single-page-app tracking), "fpc" (First Party Collector)
        - "automatic_scroll_tracking" (value is {"is_enabled": bool, "thresholds": [unique ints 0-100]});
          thresholds are always required (even when disabling) — a common default is [5, 50, 95].
        - Hostnames (value is a string): "tracking_domain", "static_resources_domain", "ui_apis_domain"
        - Paths (value is a string): "container_js_path", "tracking_script_path", "tracking_endpoint_path"

        Use tools_parameters_get("container_settings_app_update") to get the complete JSON schema,
        including the exact value shape of every supported setting.

        Args:
            app_id: UUID of the app (required; ask the user for it if not provided)
            attributes: Object with a ``data`` list, each item ``{"id": <setting_name>, "value": <value>}``.

        Returns:
            Dictionary containing update status:
            - status: Update status
            - message: Descriptive message
            - updated_fields: List of setting names that were updated

        Examples:
            # "please enable automatic scroll tracking"
            attributes = {"data": [
                {"id": "automatic_scroll_tracking", "value": {"is_enabled": true, "thresholds": [5, 50, 95]}}
            ]}

            # "turn off spa tracking"
            attributes = {"data": [{"id": "spa_tracking", "value": {"is_enabled": false}}]}

            # "set up tracking domain to test.com"
            attributes = {"data": [{"id": "tracking_domain", "value": "test.com"}]}

            # "serve the container from our own (reverse-proxied) domain analytics.example.com
            # under /js/container.js" — a custom, unregistered domain, so enable fpc as well
            attributes = {"data": [
                {"id": "fpc", "value": {"is_enabled": true}},
                {"id": "tracking_domain", "value": "analytics.example.com"},
                {"id": "container_js_path", "value": "/js/container.js"},
            ]}
        """
        return update_container_settings(app_id, attributes)

    @mcp.tool(annotations={"title": "Piwik PRO: Delete Container Setting"})
    def container_settings_app_delete(app_id: str, setting_name: str) -> OperationStatusResponse:
        """Delete a container setting for an app, reverting it to the organization/default value.

        Args:
            app_id: UUID of the app
            setting_name: Name of the container setting to remove (e.g. "automatic_scroll_tracking")

        Returns:
            Dictionary containing deletion status:
            - status: "success" if deletion was successful
            - message: Descriptive message about the deletion
        """
        return delete_container_setting(app_id, setting_name)
