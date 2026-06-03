"""
Trigger management tools for Piwik PRO Tag Manager.

This module provides MCP tools for managing triggers, including creation,
updating, listing, and detailed information retrieval.
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
from ...responses import CopyResourceResponse, OperationStatusResponse
from .models import TriggerCreateAttributes, TriggerRelationships, TriggerUpdateAttributes


def _mcp_relationships_to_api_payload(relationships: dict[str, Any] | None) -> dict[str, Any] | None:
    """Build JSON:API ``data.relationships`` from the MCP ``relationships`` argument.

    Only ``triggers`` and ``tags`` are allowed (see ``TriggerRelationships``). They are validated
    and converted into JSON:API ``data`` arrays; omit the argument or pass an empty object when
    you have no tag or trigger links to send.
    """
    if relationships is None:
        return None
    validated = validate_data_against_model(relationships, TriggerRelationships, invalid_item_label="relationships")
    payload: dict[str, Any] = {}
    if validated.triggers is not None:
        trigger_data: list[dict[str, Any]] = []
        for member in validated.triggers:
            entry: dict[str, Any] = {"id": member.id, "type": "trigger"}
            if member.meta is not None:
                entry["meta"] = member.meta.model_dump(exclude_none=True)
            trigger_data.append(entry)
        payload["triggers"] = {"data": trigger_data}
    if validated.tags is not None:
        payload["tags"] = {"data": [{"id": tid, "type": "tag"} for tid in validated.tags]}
    return payload if payload else None


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


def create_trigger(
    app_id: str,
    attributes: dict,
    relationships: dict[str, Any] | None = None,
) -> TagManagerSingleResponse:
    """Create a trigger; conditions are evaluated with logical AND (no OR grouping)."""
    try:
        client = create_piwik_client()

        # Validate and enforce allowlist through TriggerCreateAttributes
        validated_attrs = validate_data_against_model(attributes, TriggerCreateAttributes)

        # Convert to dictionary and filter out None values
        create_kwargs = {k: v for k, v in validated_attrs.model_dump(exclude_none=True).items()}
        create_kwargs.pop("relationships", None)

        # Extract required fields
        name = create_kwargs.pop("name")
        trigger_type = create_kwargs.pop("trigger_type")

        api_rels = _mcp_relationships_to_api_payload(relationships)

        response = client.tag_manager.create_trigger(
            app_id=app_id,
            name=name,
            trigger_type=trigger_type,
            relationships=api_rels,
            **create_kwargs,
        )
        return TagManagerSingleResponse(**response)
    except BadRequestError as e:
        raise RuntimeError(f"Failed to create trigger: {e.message}")
    except Exception as e:
        raise RuntimeError(f"Failed to create trigger: {str(e)}")


def update_trigger(
    app_id: str,
    trigger_id: str,
    attributes: dict | None = None,
    relationships: dict[str, Any] | None = None,
) -> TagManagerSingleResponse:
    """Update trigger fields from attributes; request data.relationships only from the MCP relationships argument."""
    try:
        client = create_piwik_client()

        attributes = attributes if attributes is not None else {}

        validated_attrs = validate_data_against_model(attributes, TriggerUpdateAttributes)
        update_kwargs = {k: v for k, v in validated_attrs.model_dump(by_alias=True, exclude_none=True).items()}
        update_kwargs.pop("relationships", None)
        api_rels = _mcp_relationships_to_api_payload(relationships)

        if not update_kwargs and api_rels is None:
            raise RuntimeError("No editable fields provided for update")

        response = client.tag_manager.update_trigger(
            app_id=app_id,
            trigger_id=trigger_id,
            relationships=api_rels,
            **update_kwargs,
        )

        if response is None:
            updated_trigger = client.tag_manager.get_trigger(app_id=app_id, trigger_id=trigger_id)
            return TagManagerSingleResponse(**updated_trigger)

        return TagManagerSingleResponse(**response)
    except NotFoundError:
        raise RuntimeError(f"Trigger with ID {trigger_id} not found in app {app_id}")
    except BadRequestError as e:
        raise RuntimeError(f"Failed to update trigger: {e.message}")
    except Exception as e:
        raise RuntimeError(f"Failed to update trigger: {str(e)}")


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


def delete_trigger(app_id: str, trigger_id: str) -> OperationStatusResponse:
    try:
        client = create_piwik_client()
        client.tag_manager.delete_trigger(app_id, trigger_id)
        return OperationStatusResponse(
            status="success",
            message=f"Trigger {trigger_id} deleted successfully from app {app_id}",
        )
    except NotFoundError:
        raise RuntimeError(f"Trigger with ID {trigger_id} not found in app {app_id}")
    except BadRequestError as e:
        raise RuntimeError(f"Failed to delete trigger: {e.message}")
    except Exception as e:
        raise RuntimeError(f"Failed to delete trigger: {str(e)}")


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
    def triggers_create(
        app_id: str,
        attributes: dict,
        relationships: dict[str, Any] | None = None,
    ) -> TagManagerSingleResponse:
        """Create a new trigger in Piwik PRO Tag Manager using JSON attributes.

        Before calling this tool, always check both:
        - `templates_list_triggers()` and `templates_get_trigger(template_name)` for trigger type requirements
        - `tools_parameters_get("triggers_create")` for the runtime JSON schema of the `attributes` object

        Only trigger types listed by `templates_list_triggers()` are supported.

        Required workflow:
            1. templates_list_triggers() → get exact trigger type names
            2. templates_get_trigger(template_name='...') → get requirements for your chosen type
            3. triggers_create() → create the trigger with verified type name

        Args:
            relationships: Optional object with only ``tags`` and/or ``triggers`` (see tool schema).
                Converted to JSON:API ``data.relationships``; unknown keys are rejected.
        """
        return create_trigger(app_id, attributes, relationships)

    @mcp.tool(annotations={"title": "Piwik PRO: Update Trigger"})
    def triggers_update(
        app_id: str,
        trigger_id: str,
        attributes: dict | None = None,
        relationships: dict[str, Any] | None = None,
    ) -> TagManagerSingleResponse:
        """Update an existing trigger in Piwik PRO Tag Manager using JSON attributes.

        Before calling this tool, always check both:
        - `templates_get_trigger(template_name)` for trigger type requirements
        - `tools_parameters_get("triggers_update")` for the runtime JSON schema of the `attributes` object

        Only editable fields are processed. Create-only and read-only fields are ignored.

        Args:
            attributes: Optional dict of editable fields (name, conditions). If omitted, the call is treated
                as an empty update and is rejected unless `relationships` is provided.
            relationships: Same as triggers_create: only ``triggers`` and/or ``tags``; converted to JSON:API.
        """
        return update_trigger(app_id, trigger_id, attributes, relationships)

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

    @mcp.tool(annotations={"title": "Piwik PRO: Delete Trigger"})
    def triggers_delete(app_id: str, trigger_id: str) -> OperationStatusResponse:
        """Delete a trigger from Piwik PRO Tag Manager.

        Warning: This action is irreversible.
        """
        return delete_trigger(app_id, trigger_id)

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
