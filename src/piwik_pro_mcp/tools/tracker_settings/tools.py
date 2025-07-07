"""
Tracker settings management tools for Piwik PRO.

This module provides MCP tools for managing tracker settings,
including global and app-specific settings.
"""

from mcp.server.fastmcp import FastMCP

from piwik_pro_mcp.api.exceptions import BadRequestError, NotFoundError
from piwik_pro_mcp.api.methods.tracker_settings.models import AppTrackerSettings, GlobalTrackerSettings

from ...common.utils import create_piwik_client, validate_data_against_model
from ...responses import OperationStatusResponse, TrackerSettingsResponse, UpdateStatusResponse


def get_global_tracker_settings() -> TrackerSettingsResponse:
    try:
        client = create_piwik_client()
        response = client.tracker_settings.get_global_settings()

        # Extract attributes from JSON:API response
        attributes = response.get("data", {}).get("attributes", {})

        return TrackerSettingsResponse(**attributes)
    except Exception as e:
        raise RuntimeError(f"Failed to get global tracker settings: {str(e)}")


def update_global_tracker_settings(attributes: dict) -> UpdateStatusResponse:
    try:
        client = create_piwik_client()

        validated_attrs = validate_data_against_model(attributes, GlobalTrackerSettings)

        # Convert to dictionary and filter out None values
        update_kwargs = {k: v for k, v in validated_attrs.model_dump(by_alias=True, exclude_none=True).items()}

        if not update_kwargs:
            raise RuntimeError("No update parameters provided")

        updated_fields = list(update_kwargs.keys())
        client.tracker_settings.update_global_settings(**update_kwargs)

        return UpdateStatusResponse(
            status="success",
            message="Global tracker settings updated successfully",
            updated_fields=updated_fields,
        )
    except BadRequestError as e:
        raise RuntimeError(f"Failed to update global tracker settings: {e.message}")
    except Exception as e:
        raise RuntimeError(f"Failed to update global tracker settings: {str(e)}")


def get_app_tracker_settings(app_id: str) -> TrackerSettingsResponse:
    try:
        client = create_piwik_client()
        response = client.tracker_settings.get_app_settings(app_id)

        # Extract attributes from JSON:API response
        attributes = response.get("data", {}).get("attributes", {})

        return TrackerSettingsResponse(**attributes)
    except NotFoundError:
        raise RuntimeError(f"App with ID {app_id} not found")
    except Exception as e:
        raise RuntimeError(f"Failed to get app tracker settings: {str(e)}")


def update_app_tracker_settings(app_id: str, attributes: dict) -> UpdateStatusResponse:
    try:
        client = create_piwik_client()

        # Validate attributes directly against the model
        validated_attrs = validate_data_against_model(attributes, AppTrackerSettings)

        # Convert to dictionary and filter out None values
        update_kwargs = {k: v for k, v in validated_attrs.model_dump(by_alias=True, exclude_none=True).items()}

        if not update_kwargs:
            raise RuntimeError("No update parameters provided")

        updated_fields = list(update_kwargs.keys())
        client.tracker_settings.update_app_settings(app_id, **update_kwargs)

        return UpdateStatusResponse(
            status="success",
            message=f"App {app_id} tracker settings updated successfully",
            updated_fields=updated_fields,
        )
    except NotFoundError:
        raise RuntimeError(f"App with ID {app_id} not found")
    except BadRequestError as e:
        raise RuntimeError(f"Failed to update app tracker settings: {e.message}")
    except Exception as e:
        raise RuntimeError(f"Failed to update app tracker settings: {str(e)}")


def delete_app_tracker_setting(app_id: str, setting: str) -> OperationStatusResponse:
    try:
        client = create_piwik_client()
        client.tracker_settings.delete_app_setting(app_id, setting)

        return OperationStatusResponse(
            status="success",
            message=f"Tracker setting '{setting}' deleted successfully for app {app_id}",
        )
    except NotFoundError:
        raise RuntimeError(f"App with ID {app_id} or setting '{setting}' not found")
    except Exception as e:
        raise RuntimeError(f"Failed to delete app tracker setting: {str(e)}")


def register_tracker_settings_tools(mcp: FastMCP) -> None:
    """Register all tracker settings tools with the MCP server."""

    @mcp.tool(annotations={"title": "Piwik PRO: Get Global Tracker Settings", "readOnlyHint": True})
    def tracker_settings_global_get() -> TrackerSettingsResponse:
        """Get global tracker settings.

        Returns:
            Dictionary containing global tracker settings including:
            - anonymize_visitor_ip_level: IP anonymization level (0-3)
            - excluded_ips: List of IPs excluded from tracking
            - excluded_url_params: URL parameters excluded from tracking
            - excluded_user_agents: User agents excluded from tracking
            - site_search_query_params: Site search query parameters
            - site_search_category_params: Site search category parameters
            - visitor_geolocation_based_on_anonymized_ip: Geolocation based on anonymized IP
            - updated_at: Last modification timestamp
        """
        return get_global_tracker_settings()

    @mcp.tool(annotations={"title": "Piwik PRO: Update Global Tracker Settings"})
    def tracker_settings_global_update(attributes: dict) -> UpdateStatusResponse:
        """Update global tracker settings using JSON attributes.

        This tool uses a simplified interface with a single `attributes` parameter.
        Use tools_parameters_get("tracker_settings_global_update") to get
        the complete JSON schema with all available fields, types, and validation rules.

        Args:
            attributes: Dictionary containing global tracker settings attributes to update.
                       All fields are optional. Supported fields include anonymize_visitor_ip_level,
                       excluded_ips, excluded_url_params, site_search_query_params, and more.

        Returns:
            Dictionary containing update status:
            - status: Update status
            - message: Descriptive message
            - updated_fields: List of fields that were updated

        Parameter Discovery:
            Use tools_parameters_get("tracker_settings_global_update") to get
            the complete JSON schema for all available fields. This returns validation rules,
            field types, and examples.

        Examples:
            # Get available parameters first
            schema = tools_parameters_get("tracker_settings_global_update")

            # Update IP anonymization level
            attributes = {"anonymize_visitor_ip_level": 2}

            # Update multiple settings
            attributes = {
                "anonymize_visitor_ip_level": 2,
                "excluded_ips": ["192.168.1.1", "10.0.0.1"],
                "excluded_url_params": ["utm_source", "utm_medium"]
            }
        """
        return update_global_tracker_settings(attributes)

    @mcp.tool(annotations={"title": "Piwik PRO: Get App Tracker Settings", "readOnlyHint": True})
    def tracker_settings_app_get(app_id: str) -> TrackerSettingsResponse:
        """Get tracker settings for a specific app.

        Args:
            app_id: UUID of the app

        Returns:
            Dictionary containing app tracker settings including:
            - anonymize_visitor_geolocation_level: Geolocation anonymization level
            - anonymize_visitor_ip_level: IP anonymization level (0-4)
            - campaign_*_params: Campaign tracking parameters
            - session_* settings: Session handling configuration
            - excluded_ips: IPs excluded from tracking
            - excluded_user_agents: User agents excluded from tracking
            - Various tracking and privacy settings
            - updated_at: Last modification timestamp
        """
        return get_app_tracker_settings(app_id)

    @mcp.tool(annotations={"title": "Piwik PRO: Update App Tracker Settings"})
    def tracker_settings_app_update(app_id: str, attributes: dict) -> UpdateStatusResponse:
        """Update tracker settings for a specific app using JSON attributes.

        This tool uses a simplified interface with 2 parameters: app_id and attributes.
        Use tools_parameters_get("tracker_settings_app_update") to get
        the complete JSON schema with all available fields, types, and validation rules.

        Args:
            app_id: UUID of the app
            attributes: Dictionary containing tracker settings attributes to update. All fields
                       are optional. Supported fields include anonymize_visitor_ip_level,
                       excluded_ips, session settings, campaign parameters, and more.

        Returns:
            Dictionary containing update status:
            - status: Update status
            - message: Descriptive message
            - updated_fields: List of fields that were updated

        Parameter Discovery:
            Use tools_parameters_get("tracker_settings_app_update") to get
            the complete JSON schema for all available fields. This returns validation rules,
            field types, and examples.

        Examples:
            # Get available parameters first
            schema = tools_parameters_get("tracker_settings_app_update")

            # Update basic settings
            attributes = {
                "anonymize_visitor_ip_level": 2,
                "excluded_ips": ["192.168.1.1", "10.0.0.1"]
            }

            # Update session and campaign settings
            attributes = {
                "session_max_duration_seconds": 3600,
                "campaign_name_params": ["utm_campaign", "campaign"],
                "exclude_crawlers": True
            }
        """
        return update_app_tracker_settings(app_id, attributes)

    @mcp.tool(annotations={"title": "Piwik PRO: Delete App Tracker Setting"})
    def tracker_settings_app_delete(app_id: str, setting: str) -> OperationStatusResponse:
        """Delete a specific tracker setting for an app.

        This causes the setting to revert to the global setting.

        Args:
            app_id: UUID of the app
            setting: Name of the tracker setting to delete

        Returns:
            Dictionary containing deletion status:
            - status: "success" if deletion was successful
            - message: Descriptive message about the deletion
        """
        return delete_app_tracker_setting(app_id, setting)
