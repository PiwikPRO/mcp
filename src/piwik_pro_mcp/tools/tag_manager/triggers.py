"""
Trigger management tools for Piwik PRO Tag Manager.

This module provides MCP tools for managing triggers, including creation,
listing, and detailed information retrieval.
"""

from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP

from piwik_pro_mcp.api.exceptions import BadRequestError, NotFoundError
from piwik_pro_mcp.api.methods.tag_manager.models import (
    TagManagerListResponse,
    TagManagerSingleResponse,
    TriggerFilters,
)

from ...common.utils import create_piwik_client, validate_data_against_model
from ...responses import CopyResourceResponse
from .models import TriggerCreateAttributes


def list_triggers(
    app_id: str,
    limit: int = 10,
    offset: int = 0,
    filters: Optional[Dict[str, Any]] = None,
) -> TagManagerListResponse:
    if filters is not None:
        filters = validate_data_against_model(filters, TriggerFilters, invalid_item_label="filter")
    try:
        client = create_piwik_client()
        response = client.tag_manager.list_triggers(
            app_id=app_id,
            limit=limit,
            offset=offset,
            filters=filters,
        )
        return TagManagerListResponse(**response)
    except Exception as e:
        raise RuntimeError(f"Failed to list triggers: {str(e)}")


def get_trigger(app_id: str, trigger_id: str) -> TagManagerSingleResponse:
    try:
        client = create_piwik_client()
        response = client.tag_manager.get_trigger(app_id, trigger_id)
        return TagManagerSingleResponse(**response)
    except NotFoundError:
        raise RuntimeError(f"Trigger with ID {trigger_id} not found in app {app_id}")
    except Exception as e:
        raise RuntimeError(f"Failed to get trigger: {str(e)}")


def create_trigger(app_id: str, attributes: dict) -> TagManagerSingleResponse:
    """Create a trigger; conditions are evaluated with logical AND (no OR grouping)."""
    try:
        client = create_piwik_client()

        # Validate and enforce allowlist through TriggerCreateAttributes
        validated_attrs = validate_data_against_model(attributes, TriggerCreateAttributes)

        # Convert to dictionary and filter out None values
        create_kwargs = {k: v for k, v in validated_attrs.model_dump(exclude_none=True).items()}

        # Extract required fields
        name = create_kwargs.pop("name")
        trigger_type = create_kwargs.pop("trigger_type")

        response = client.tag_manager.create_trigger(
            app_id=app_id, name=name, trigger_type=trigger_type, **create_kwargs
        )
        return TagManagerSingleResponse(**response)
    except BadRequestError as e:
        raise RuntimeError(f"Failed to create trigger: {e.message}")
    except Exception as e:
        raise RuntimeError(f"Failed to create trigger: {str(e)}")


def copy_trigger(
    app_id: str,
    trigger_id: str,
    target_app_id: Optional[str] = None,
    name: Optional[str] = None,
) -> CopyResourceResponse:
    try:
        client = create_piwik_client()
        response = client.tag_manager.copy_trigger(
            app_id=app_id,
            trigger_id=trigger_id,
            name=name,
            target_app_id=target_app_id,
        )

        if response is None:
            raise RuntimeError("Empty response from API while copying trigger")

        data: Dict[str, Any] = response.get("data", {})
        relationships: Dict[str, Any] = data.get("relationships", {})
        operation = relationships.get("operation", {}).get("data", {})

        # name is available in response.attributes for trigger copy, but keep consistent API
        resp_name = name
        if "attributes" in data and isinstance(data["attributes"], dict):
            resp_name = data["attributes"].get("name", name)

        return CopyResourceResponse(
            resource_id=data.get("id", ""),
            resource_type=data.get("type", "trigger"),
            operation_id=operation.get("id", ""),
            copied_into_app_id=target_app_id or app_id,
            name=resp_name,
        )
    except NotFoundError:
        raise RuntimeError(f"Trigger with ID {trigger_id} not found in app {app_id}")
    except BadRequestError as e:
        raise RuntimeError(f"Failed to copy trigger: {e.message}")
    except Exception as e:
        raise RuntimeError(f"Failed to copy trigger: {str(e)}")


def register_trigger_tools(mcp: FastMCP) -> None:
    """Register all trigger management tools with the MCP server."""

    @mcp.tool(annotations={"title": "Piwik PRO: List Triggers", "readOnlyHint": True})
    def triggers_list(
        app_id: str,
        limit: int = 10,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None,
    ) -> TagManagerListResponse:
        """List triggers for an app in Piwik PRO Tag Manager.

        Args:
            app_id: UUID of the app
            limit: Maximum number of triggers to return (default: 10)
            offset: Number of triggers to skip (default: 0)
            filter_template: Filter by template names
            filter_is_active: Filter by active status

        Returns:
            Dictionary containing trigger list and metadata including:
            - data: List of trigger objects with id, name, template, and attributes
            - meta: Metadata with pagination information
        """
        return list_triggers(
            app_id=app_id,
            limit=limit,
            offset=offset,
            filters=filters,
        )

    @mcp.tool(annotations={"title": "Piwik PRO: Get Trigger", "readOnlyHint": True})
    def triggers_get(app_id: str, trigger_id: str) -> TagManagerSingleResponse:
        """Get detailed information about a specific trigger.

        Args:
            app_id: UUID of the app
            trigger_id: UUID of the trigger

        Returns:
            Dictionary containing trigger details including:
            - data: Trigger object with id, name, template, and all attributes
            - Trigger conditions and configuration

        Related Tools:
            - piwik_get_trigger_tags() - See what tags are assigned to this trigger
        """
        return get_trigger(app_id, trigger_id)

    @mcp.tool(annotations={"title": "Piwik PRO: Create Trigger"})
    def triggers_create(app_id: str, attributes: dict) -> TagManagerSingleResponse:
        """Create a new trigger in Piwik PRO Tag Manager using JSON attributes.

        Only trigger types listed by `templates_list_triggers()` are supported. Any other type will be refused.

        💡 TIP: Use these tools to discover available trigger templates and their requirements:
        - templates_list_triggers() - List all available trigger templates
        - templates_get_trigger(template_name='page_view') - Get detailed requirements

        This tool uses a simplified interface with 2 parameters: app_id and attributes.
        Use tools_parameters_get("triggers_create") to get the complete JSON schema
        with all available fields, types, and validation rules.

        Args:
            app_id: UUID of the app
            attributes: Dictionary containing trigger attributes for creation. Required fields vary by trigger type:
                       - name: Trigger name (always required)
                       - trigger_type: Trigger type (e.g., 'page_view', 'click', 'form_submission')
                       - conditions: Array of condition objects that define when trigger fires
                         - evaluated with logical AND only, OR groupings are not supported
                       - Additional fields may be required depending on trigger type

        Returns:
            Dictionary containing created trigger information including:
            - data: Created trigger object with id, name, trigger_type, and attributes
            - Trigger conditions and configuration

        Template Discovery:
            Use templates_list_triggers() to see all available trigger templates, or
            templates_get_trigger(template_name='TEMPLATE') for specific requirements.

        Parameter Discovery:
            Use tools_parameters_get("triggers_create") to get the complete JSON schema
            for all available fields. This returns validation rules, field types, and examples.

        Examples:
            # Get available trigger templates first
            templates = templates_list_triggers()

            # Get specific template requirements
            page_view_info = templates_get_trigger(template_name='page_view')

            # Create page view trigger
            attributes = {
                "name": "Homepage Page View",
                "trigger_type": "page_view",
                "conditions": [
                    {
                        "variable_id": "page-path-variable-uuid",
                        "condition_type": "equals",
                        "value": "/",
                        "options": {}
                    }
                ]
            }

            # Create click trigger
            attributes = {
                "name": "CTA Button Click",
                "trigger_type": "click",
                "conditions": [
                    {
                        "variable_id": "click-element-variable-uuid",
                        "condition_type": "equals",
                        "value": "#cta-primary",
                        "options": {"selector_type": "css"}
                    }
                ]
            }
        """
        return create_trigger(app_id, attributes)

    @mcp.tool(annotations={"title": "Piwik PRO: Copy Trigger"})
    def triggers_copy(
        app_id: str,
        trigger_id: str,
        target_app_id: Optional[str] = None,
        name: Optional[str] = None,
    ) -> CopyResourceResponse:
        """Copy a trigger, optionally to another app.

        Args:
            app_id: UUID of the source app
            trigger_id: UUID of the trigger to copy
            target_app_id: Optional UUID of the target app. If omitted, copies within the same app.
            name: Optional new name for the copied trigger

        Returns:
            Normalized copy response including new resource id and operation id.
        """
        return copy_trigger(app_id, trigger_id, target_app_id, name)
