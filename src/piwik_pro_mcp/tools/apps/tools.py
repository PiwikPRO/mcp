"""
App management MCP tools.

This module provides MCP tool functions for managing Piwik PRO apps,
including creation, updating, listing, and deletion of apps.
"""

from typing import Optional

from mcp.server.fastmcp import FastMCP

from piwik_pro_mcp.api.exceptions import BadRequestError, NotFoundError
from piwik_pro_mcp.api.methods.apps.models import AppEditableAttributes, NewAppAttributes

from ...common.utils import create_piwik_client, validate_data_against_model
from ...responses import (
    OperationStatusResponse,
    UpdateStatusResponse,
)
from .models import (
    AppCreateMCPResponse,
    AppDetailsMCPResponse,
    AppListMCPResponse,
    AppSummary,
)


def list_apps(limit: int = 100, offset: int = 0, search: Optional[str] = None) -> AppListMCPResponse:
    try:
        client = create_piwik_client()
        response = client.apps.list_apps(limit=limit, offset=offset, search=search)

        # Extract relevant information and convert to AppSummary models
        apps_data = []
        for app in response.get("data", []):
            app_summary = AppSummary(
                id=app["id"],
                name=app["attributes"]["name"],
                created_at=app["attributes"].get("addedAt"),
                updated_at=app["attributes"].get("updatedAt"),
            )
            apps_data.append(app_summary)

        return AppListMCPResponse(
            apps=apps_data,
            total=response.get("meta", {}).get("total", 0),
            limit=limit,
            offset=offset,
        )

    except Exception as e:
        raise RuntimeError(f"Failed to list apps: {str(e)}")


def get_app_details(app_id: str) -> AppDetailsMCPResponse:
    try:
        client = create_piwik_client()
        response = client.apps.get_app(app_id)

        app_data = response["data"]
        attrs = app_data["attributes"]

        return AppDetailsMCPResponse(
            id=app_data["id"],
            name=attrs["name"],
            urls=attrs["urls"],
            app_type=attrs.get("appType"),
            timezone=attrs.get("timezone"),
            currency=attrs.get("currency"),
            gdpr_enabled=attrs.get("gdpr"),
            gdpr_data_anonymization=attrs.get("gdprDataAnonymization"),
            real_time_dashboards=attrs.get("realTimeDashboards"),
            created_at=attrs.get("addedAt"),
            updated_at=attrs.get("updatedAt"),
        )

    except NotFoundError:
        raise RuntimeError(f"App with ID {app_id} not found")
    except Exception as e:
        raise RuntimeError(f"Failed to get app details: {str(e)}")


def create_app(attributes: dict) -> AppCreateMCPResponse:
    try:
        client = create_piwik_client()

        # Validate attributes directly against the model
        validated_attrs = validate_data_against_model(attributes, NewAppAttributes)

        # Convert to dictionary and filter out None values
        create_kwargs = {k: v for k, v in validated_attrs.model_dump(by_alias=True, exclude_none=True).items()}

        # Extract required fields
        name = create_kwargs.pop("name")
        urls = create_kwargs.pop("urls")

        response = client.apps.create_app(name=name, urls=urls, **create_kwargs)

        app_data = response["data"]
        attrs = app_data["attributes"]

        return AppCreateMCPResponse(
            id=app_data["id"],
            name=attrs["name"],
            urls=attrs["urls"],
            timezone=attrs.get("timezone"),
            currency=attrs.get("currency"),
            gdpr_enabled=attrs.get("gdpr"),
            created_at=attrs.get("addedAt"),
        )

    except BadRequestError as e:
        raise RuntimeError(f"Failed to create app: {e.message}")
    except Exception as e:
        raise RuntimeError(f"Failed to create app: {str(e)}")


def update_app(app_id: str, attributes: dict) -> UpdateStatusResponse:
    try:
        client = create_piwik_client()

        # Validate attributes directly against the model
        validated_attrs = validate_data_against_model(attributes, AppEditableAttributes)  # noqa: F821

        # Convert to dictionary and filter out None values
        update_kwargs = {k: v for k, v in validated_attrs.model_dump(by_alias=True, exclude_none=True).items()}

        if not update_kwargs:
            raise RuntimeError("No update parameters provided")

        updated_fields = list(update_kwargs.keys())
        client.apps.update_app(app_id=app_id, **update_kwargs)

        return UpdateStatusResponse(
            status="success",
            message=f"App {app_id} updated successfully",
            updated_fields=updated_fields,
        )

    except NotFoundError:
        raise RuntimeError(f"App with ID {app_id} not found")
    except BadRequestError as e:
        raise RuntimeError(f"Failed to update app: {e.message}")
    except Exception as e:
        raise RuntimeError(f"Failed to update app: {str(e)}")


def delete_app(app_id: str) -> OperationStatusResponse:
    try:
        client = create_piwik_client()
        client.apps.delete_app(app_id)

        return OperationStatusResponse(status="success", message=f"App {app_id} deleted successfully")

    except NotFoundError:
        raise RuntimeError(f"App with ID {app_id} not found")
    except BadRequestError as e:
        raise RuntimeError(f"Failed to delete app: {e.message}")
    except Exception as e:
        raise RuntimeError(f"Failed to delete app: {str(e)}")


def register_app_tools(mcp: FastMCP) -> None:
    """Register all app management tools with the MCP server."""

    @mcp.tool(annotations={"title": "Piwik PRO: List Apps", "readOnlyHint": True})
    def apps_list(limit: int = 100, offset: int = 0, search: Optional[str] = None) -> AppListMCPResponse:
        """List apps from Piwik PRO analytics.

        Retrieves a list of applications (websites/apps) that are being tracked
        in the Piwik PRO analytics platform.

        Args:
            limit: Maximum number of apps to return (default: 100, max: 1000)
            offset: Number of apps to skip (default: 0)
            search: Search query to filter apps by name

        Returns:
            Dictionary containing app list and metadata including:
            - apps: List of app objects with id, name, urls, timezone, currency, etc.
            - total: Total number of apps available
            - limit: Number of apps requested
            - offset: Number of apps skipped
        """
        return list_apps(limit=limit, offset=offset, search=search)

    @mcp.tool(annotations={"title": "Piwik PRO: Get App", "readOnlyHint": True})
    def apps_get(app_id: str) -> AppDetailsMCPResponse:
        """Get detailed information about a specific app.

        Args:
            app_id: UUID of the app to retrieve

        Returns:
            Dictionary containing detailed app information including:
            - id: App UUID
            - name: App name
            - urls: List of URLs where the app is available
            - app_type: Type of application
            - timezone: App timezone
            - currency: App currency
            - gdpr_enabled: Whether GDPR is enabled
            - gdpr_data_anonymization: Whether GDPR data anonymization is enabled
            - real_time_dashboards: Whether real-time dashboards are enabled
            - created_at: App creation datetime
            - updated_at: App last update datetime

        For more details use also get_app_tracker_settings tool.
        """
        return get_app_details(app_id)

    @mcp.tool(annotations={"title": "Piwik PRO: Create App"})
    def apps_create(attributes: dict) -> AppCreateMCPResponse:
        """Create a new app in Piwik PRO analytics using JSON attributes.

        Use tools_parameters_get("apps_create") tool to get the complete
        JSON schema with all available fields, types, and validation rules.

        Args:
            attributes: Dictionary containing app attributes for creation.
                        Required fields are 'name' and 'urls'. All other fields are optional.

        Returns:
            Dictionary containing created app information including:
            - id: Generated app UUID
            - name: App name
            - urls: List of URLs
            - timezone: App timezone
            - currency: App currency
            - gdpr_enabled: GDPR status
            - created_at: Creation datetime
            - updated_at: Last update datetime

        Parameter Discovery:
            Use list_available_parameters("piwik_create_app") to get the complete JSON schema
            for all available fields. This returns validation rules, field types, and examples.

        Examples:
            # Get available parameters first
            schema = tools_parameters_get("apps_create")

            # Create app with minimal required fields
            attributes = {"name": "My App", "urls": ["https://example.com"]}

            # Create app with additional settings
            attributes = {
                "name": "My App",
                "urls": ["https://example.com"],
                "timezone": "America/New_York",
                "currency": "EUR",
                "gdpr": True
            }
        """
        return create_app(attributes)

    @mcp.tool(annotations={"title": "Piwik PRO: Update App"})
    def apps_update(app_id: str, attributes: dict) -> UpdateStatusResponse:
        """Update an existing app in Piwik PRO analytics using JSON attributes.

        This tool uses a simplified interface with 2 parameters: app_id and attributes.
        Use tools_parameters_get("apps_update") to get the complete JSON schema
        with all available fields, types, and validation rules.

        Args:
            app_id: UUID of the app to update
            attributes: Dictionary containing app attributes to update. All fields are optional.
                      Supported fields include name, urls, timezone, currency, gdpr, and more.

        Returns:
            Dictionary containing update status:
            - status: "success" if update was successful
            - message: Descriptive message about the update
            - updated_fields: List of fields that were updated

        Parameter Discovery:
            Use list_available_parameters("piwik_update_app") to get the complete JSON schema
            for all available fields. This returns validation rules, field types, and examples.

        Examples:
            # Get available parameters first
            schema = tools_parameters_get("apps_update")

            # Update app name and timezone
            attributes = {"name": "New App Name", "timezone": "America/New_York"}

            # Update multiple fields
            attributes = {"name": "Updated App", "urls": ["https://example.com"], "gdpr": true}
        """
        return update_app(app_id, attributes)

    @mcp.tool(annotations={"title": "Piwik PRO: Delete App"})
    def apps_delete(app_id: str) -> OperationStatusResponse:
        """Delete an app from Piwik PRO analytics.

        Warning: This action is irreversible and will permanently delete
        all data associated with the app.

        Args:
            app_id: UUID of the app to delete

        Returns:
            Dictionary containing deletion status:
            - status: "success" if deletion was successful
            - message: Descriptive message about the deletion
        """
        return delete_app(app_id)
