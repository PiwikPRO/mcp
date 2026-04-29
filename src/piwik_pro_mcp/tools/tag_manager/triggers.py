"""
Trigger management tools for Piwik PRO Tag Manager.

This module provides MCP tools for managing triggers, including creation,
listing, and detailed information retrieval.
"""

from typing import Any

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
    filters: dict[str, Any] | None = None,
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
    limit: int | None = None,
    offset: int | None = None,
    sort: str | None = None,
    name: str | None = None,
    is_active: bool | None = None,
    template: str | None = None,
    consent_type: str | None = None,
    is_prioritized: bool | None = None,
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
    target_app_id: str | None = None,
    name: str | None = None,
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

        data: dict[str, Any] = response.get("data", {})
        relationships: dict[str, Any] = data.get("relationships", {})
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
        filters: dict[str, Any] | None = None,
    ) -> TagManagerListResponse:
        """List triggers for an app in Piwik PRO Tag Manager.

        Args:
            app_id: UUID of the app
            limit: Maximum number of triggers to return (default: 10)
            offset: Number of triggers to skip (default: 0)
            filters: Optional filter keys: name, trigger_type, has_any_tags,
                has_any_condition_with_audience, condition_with_audience_id
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

        Related Tools:
            - triggers_list_tags(app_id, trigger_id) - See what tags are assigned to this trigger
        """
        return get_trigger(app_id, trigger_id)

    @mcp.tool(annotations={"title": "Piwik PRO: Create Trigger"})
    def triggers_create(app_id: str, attributes: dict) -> TagManagerSingleResponse:
        """Create a new trigger in Piwik PRO Tag Manager using JSON attributes.

        Before calling this tool, always check both:
        - `templates_list_triggers()` and `templates_get_trigger(template_name)` for trigger type requirements
        - `tools_parameters_get("triggers_create")` for the runtime JSON schema of the `attributes` object

        Only trigger types listed by `templates_list_triggers()` are supported.

        Required workflow:
            1. templates_list_triggers() → get exact trigger type names
            2. templates_get_trigger(template_name='...') → get requirements for your chosen type
            3. triggers_create() → create the trigger with verified type name
        """
        return create_trigger(app_id, attributes)

    @mcp.tool(annotations={"title": "Piwik PRO: Copy Trigger"})
    def triggers_copy(
        app_id: str,
        trigger_id: str,
        target_app_id: str | None = None,
        name: str | None = None,
    ) -> CopyResourceResponse:
        """Copy a trigger, optionally to another app.

        Args:
            target_app_id: Optional UUID of the target app. If omitted, copies within the same app.
        """
        return copy_trigger(app_id, trigger_id, target_app_id, name)

    @mcp.tool(annotations={"title": "Piwik PRO: List Tags for Trigger", "readOnlyHint": True})
    def triggers_list_tags(
        app_id: str,
        trigger_id: str,
        limit: int | None = None,
        offset: int | None = None,
        sort: str | None = None,
        name: str | None = None,
        is_active: bool | None = None,
        template: str | None = None,
        consent_type: str | None = None,
        is_prioritized: bool | None = None,
    ) -> dict:
        """Get list of tags assigned to a specific trigger.

        Args:
            app_id: UUID of the app
            trigger_id: UUID of the trigger
            limit: Maximum number of tags to return
            offset: Number of tags to skip
            sort: Sort order - 'name', '-name', 'created_at', '-created_at', etc.
            name: Filter by tag name (partial match)
            is_active: Filter by active status
            template: Filter by tag template
            consent_type: Filter by consent type
            is_prioritized: Filter by prioritized status
        """
        return get_trigger_tags(
            app_id, trigger_id, limit, offset, sort, name, is_active, template, consent_type, is_prioritized
        )
