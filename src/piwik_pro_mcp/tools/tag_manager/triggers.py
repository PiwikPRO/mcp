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


def get_trigger_tags(
    app_id: str,
    trigger_id: str,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    sort: Optional[str] = None,
    name: Optional[str] = None,
    is_active: Optional[bool] = None,
    template: Optional[str] = None,
    consent_type: Optional[str] = None,
    is_prioritized: Optional[bool] = None,
) -> TagManagerListResponse:
    try:
        client = create_piwik_client()
        tag_manager = client.tag_manager

        # Build filters dictionary
        filters = {}
        if name is not None:
            filters["name"] = name
        if is_active is not None:
            filters["is_active"] = is_active
        if template is not None:
            filters["template"] = template
        if consent_type is not None:
            filters["consent_type"] = consent_type
        if is_prioritized is not None:
            filters["is_prioritized"] = is_prioritized

        # Get tags for the trigger
        result = tag_manager.get_trigger_tags(
            app_id=app_id, trigger_id=trigger_id, limit=limit, offset=offset, sort=sort, **filters
        )

        if result is None:
            return TagManagerListResponse(data=[], meta={"total": 0})

        return TagManagerListResponse(**result)

    except Exception as e:
        error_msg = f"Failed to get tags for trigger: {str(e)}"
        if "not found" in str(e).lower():
            error_msg = f"Trigger with ID '{trigger_id}' not found in app '{app_id}'"
        elif "bad request" in str(e).lower():
            error_msg = f"Invalid parameters provided: {str(e)}"
        raise RuntimeError(error_msg) from e


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
            - triggers_list_tags() - See what tags are assigned to this trigger
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

    @mcp.tool(annotations={"title": "Piwik PRO: List Tags for Trigger", "readOnlyHint": True})
    def triggers_list_tags(
        app_id: str,
        trigger_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        name: Optional[str] = None,
        is_active: Optional[bool] = None,
        template: Optional[str] = None,
        consent_type: Optional[str] = None,
        is_prioritized: Optional[bool] = None,
    ) -> dict:
        """Get list of tags assigned to a specific trigger.

        This tool helps you understand what tags will be fired when a specific trigger condition is met,
        which is essential for debugging and managing trigger behavior.

        Args:
            app_id: UUID of the app
            trigger_id: UUID of the trigger to get tags for
            limit: Maximum number of tags to return (optional)
            offset: Number of tags to skip for pagination (optional)
            sort: Sort order. Options: 'name', '-name', 'created_at', '-created_at', 'updated_at', '-updated_at'
            name: Filter by tag name (partial match)
            is_active: Filter by active status (true/false)
            template: Filter by tag template (e.g. 'piwik', 'custom_tag', 'google_analytics')
            consent_type: Filter by consent type ('not_require_consent', 'require_consent',
                'require_consent_for_cookie')
            is_prioritized: Filter by prioritized status (true/false)

        Returns:
            Dictionary containing:
            - data: List of tag objects assigned to the trigger
            - meta: Pagination and total count information
            - Each tag includes: id, name, template, is_active, and other attributes

        Examples:
            # Get all tags for a trigger
            triggers_list_tags(app_id="123", trigger_id="456")

            # Get only active custom tags with pagination
            triggers_list_tags(
                app_id="123",
                trigger_id="456",
                limit=10,
                is_active=True,
                template="custom_tag"
            )
        """
        return get_trigger_tags(
            app_id, trigger_id, limit, offset, sort, name, is_active, template, consent_type, is_prioritized
        )
