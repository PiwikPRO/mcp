"""
Tracker settings management tools for Piwik PRO.

This module provides MCP tools for managing tracker settings,
including global and app-specific settings.
"""

from collections.abc import Iterable

from mcp.server.fastmcp import FastMCP

from piwik_pro_mcp.api.exceptions import BadRequestError, NotFoundError
from piwik_pro_mcp.api.methods.tracker_settings.models import AppTrackerSettings, GlobalTrackerSettings

from ...common.utils import create_piwik_client, validate_data_against_model
from ...responses import (
    OperationStatusResponse,
    TrackerSettingsAppGetResponse,
    TrackerSettingsResponse,
    UpdateStatusResponse,
)


def _annotation_is_list(annotation: object) -> bool:
    """Return True when a Pydantic field annotation represents a list value."""
    origin = getattr(annotation, "__origin__", None)
    if origin is list:
        return True

    for arg in getattr(annotation, "__args__", ()):
        if getattr(arg, "__origin__", None) is list:
            return True

    return False


ARRAY_TRACKER_SETTINGS = {
    field_name
    for field_name, field_info in AppTrackerSettings.model_fields.items()
    if field_name != "updated_at" and _annotation_is_list(field_info.annotation)
}


def _extract_attributes(response: dict | None) -> dict:
    """Extract JSON:API attributes from an API response."""
    return response.get("data", {}).get("attributes", {}) if response else {}


def _deduplicate_preserving_order(values: Iterable[str]) -> list[str]:
    """Deduplicate string values without changing their relative order."""
    return list(dict.fromkeys(values))


def _merge_array_values(app_value: list[str] | None, global_value: list[str] | None) -> list[str]:
    """Merge app and global array values, keeping app items first and removing duplicates."""
    return _deduplicate_preserving_order([*(app_value or []), *(global_value or [])])


def _resolve_app_tracker_settings(app_attributes: dict, global_attributes: dict) -> dict:
    """Resolve effective app tracker settings using app values over global defaults."""
    resolved: dict = {}

    for field_name in AppTrackerSettings.model_fields:
        app_value = app_attributes.get(field_name)
        global_value = global_attributes.get(field_name)

        if field_name == "updated_at":
            resolved[field_name] = app_value or global_value
            continue

        if field_name in ARRAY_TRACKER_SETTINGS:
            if app_value is None:
                resolved[field_name] = list(global_value or [])
            else:
                resolved[field_name] = _merge_array_values(app_value, global_value)
            continue

        resolved[field_name] = global_value if app_value is None else app_value

    return resolved


def get_global_tracker_settings() -> TrackerSettingsResponse:
    try:
        client = create_piwik_client()
        response = client.tracker_settings.get_global_settings()
        attributes = _extract_attributes(response)

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


def get_app_tracker_settings(app_id: str, detailed: bool = False) -> TrackerSettingsAppGetResponse:
    try:
        client = create_piwik_client()
        app_response = client.tracker_settings.get_app_settings(app_id)
        global_response = client.tracker_settings.get_global_settings()
        app_attributes = _extract_attributes(app_response)
        global_attributes = _extract_attributes(global_response)
        resolved_attributes = _resolve_app_tracker_settings(
            app_attributes,
            global_attributes,
        )

        response_kwargs = {"settings": TrackerSettingsResponse(**resolved_attributes)}
        if detailed:
            response_kwargs["app_settings"] = AppTrackerSettings(**app_attributes)
            response_kwargs["global_settings"] = GlobalTrackerSettings(**global_attributes)

        return TrackerSettingsAppGetResponse(**response_kwargs)
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
            - anonymize_visitor_geolocation_level: Geolocation anonymization level
            - anonymize_visitor_ip_level: IP anonymization level (0-4)
            - campaign_*_params: Campaign tracking parameters
            - session_* settings: Session handling configuration
            - excluded_ips: List of IPs excluded from tracking
            - excluded_user_agents: User agents excluded from tracking
            - site_search_query_params: Site search query parameters
            - site_search_category_params: Site search category parameters
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
                       excluded_ips, campaign_*_params, site_search_query_params, and more.

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
                "campaign_name_params": ["utm_campaign"],
                "use_session_hash": True
            }
        """
        return update_global_tracker_settings(attributes)

    @mcp.tool(annotations={"title": "Piwik PRO: Get App Tracker Settings", "readOnlyHint": True})
    def tracker_settings_app_get(app_id: str, detailed: bool = False) -> TrackerSettingsAppGetResponse:
        """Get effective tracker settings for a specific app.

        Args:
            app_id: UUID of the app
            detailed: When true, include raw app-specific and global inputs alongside resolved settings

        Returns:
            Dictionary containing:
            - settings: Resolved effective tracker settings for the app
            - app_settings: Raw app-level settings when detailed=true
            - global_settings: Raw global settings when detailed=true

            Resolution rules:
            - app-specific scalar and boolean values override global values
            - null app scalar and boolean values fall back to global values
            - app array values are merged with global array values, preserving app values first
            - use tracker_settings_global_update to change global defaults explicitly
        """
        return get_app_tracker_settings(app_id, detailed=detailed)

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
