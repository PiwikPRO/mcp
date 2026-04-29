"""
Tag management tools for Piwik PRO Tag Manager.

This module provides MCP tools for managing tags, including creation,
updating, listing, deletion, and relationship management with triggers.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP

from piwik_pro_mcp.api.exceptions import BadRequestError, NotFoundError
from piwik_pro_mcp.api.methods.tag_manager.models import TagFilters, TagManagerListResponse, TagManagerSingleResponse

from ...common.templates import list_available_assets
from ...common.utils import create_piwik_client, validate_data_against_model
from ...responses import CopyResourceResponse, OperationStatusResponse
from .models import TagManagerCreateAttributes, TagManagerUpdateAttributes


def list_tags(
    app_id: str,
    limit: int = 10,
    offset: int = 0,
    filters: dict[str, Any] | None = None,
) -> TagManagerListResponse:
    if filters is not None:
        filters = validate_data_against_model(filters, TagFilters, invalid_item_label="filter")
    try:
        client = create_piwik_client()
        response = client.tag_manager.list_tags(app_id=app_id, limit=limit, offset=offset, filters=filters)
        return TagManagerListResponse(**response)
    except Exception as e:
        raise RuntimeError(f"Failed to list tags: {str(e)}")


def get_tag(app_id: str, tag_id: str) -> TagManagerSingleResponse:
    try:
        client = create_piwik_client()
        response = client.tag_manager.get_tag(app_id, tag_id)
        return TagManagerSingleResponse(**response)
    except NotFoundError:
        raise RuntimeError(f"Tag with ID {tag_id} not found in app {app_id}")
    except Exception as e:
        raise RuntimeError(f"Failed to get tag: {str(e)}")


def get_tag_triggers(
    app_id: str,
    tag_id: str,
    limit: int | None = None,
    offset: int | None = None,
    sort: str | None = None,
    name: str | None = None,
    trigger_type: str | None = None,
) -> TagManagerListResponse:
    try:
        client = create_piwik_client()

        # Build filter arguments
        filters = {}
        if name is not None:
            filters["name"] = name
        if trigger_type is not None:
            filters["trigger_type"] = trigger_type

        response = client.tag_manager.get_tag_triggers(
            app_id=app_id, tag_id=tag_id, limit=limit, offset=offset, sort=sort, **filters
        )

        return TagManagerListResponse(**response)
    except BadRequestError as e:
        raise RuntimeError(f"Failed to get tag triggers: {e.message}")
    except Exception as e:
        raise RuntimeError(f"Failed to get tag triggers: {str(e)}")


def create_tag(app_id: str, attributes: dict, triggers: str = "") -> TagManagerSingleResponse:
    try:
        client = create_piwik_client()

        # Validate attributes directly against the model
        validated_attrs = validate_data_against_model(attributes, TagManagerCreateAttributes)

        # Convert to dictionary and filter out None values
        create_kwargs = {k: v for k, v in validated_attrs.model_dump(exclude_none=True).items()}

        # Extract required fields
        name = create_kwargs.pop("name")
        template = create_kwargs.pop("template")

        # Enforce assets-driven allowlist for tag templates via model validation (retained as a safety check)
        allowed_templates = set(list_available_assets("tag_manager/tags").keys())
        if template not in allowed_templates:
            raise RuntimeError(f"Unsupported tag template '{template}'. Use templates_list_tags() to discover options.")

        # Process triggers parameter
        trigger_ids = None
        if triggers and triggers.strip():
            # Split comma-separated trigger UUIDs and clean whitespace
            trigger_ids = [trigger_id.strip() for trigger_id in triggers.split(",") if trigger_id.strip()]

        response = client.tag_manager.create_tag(
            app_id=app_id, name=name, template=template, trigger_ids=trigger_ids, **create_kwargs
        )
        return TagManagerSingleResponse(**response)
    except BadRequestError as e:
        raise RuntimeError(f"Failed to create tag: {e.message}")
    except Exception as e:
        raise RuntimeError(f"Failed to create tag: {str(e)}")


def update_tag(app_id: str, tag_id: str, attributes: dict, triggers: str = "__unchanged__") -> TagManagerSingleResponse:
    try:
        client = create_piwik_client()

        # Validate attributes directly against the model
        validated_attrs = validate_data_against_model(attributes, TagManagerUpdateAttributes)

        # Convert to dictionary and filter out None values
        update_kwargs = {k: v for k, v in validated_attrs.model_dump(exclude_none=True).items()}

        # Process triggers parameter - only process if not the unchanged sentinel value
        trigger_ids = None
        if triggers != "__unchanged__":  # Check if triggers should be modified
            if triggers.strip():
                # Split comma-separated trigger UUIDs and clean whitespace
                trigger_ids = [trigger_id.strip() for trigger_id in triggers.split(",") if trigger_id.strip()]
            else:
                # Empty string means remove all triggers
                trigger_ids = []

        # Check if we have either attributes or triggers to update
        if not update_kwargs and trigger_ids is None:
            raise RuntimeError("No update parameters provided")

        response = client.tag_manager.update_tag(app_id=app_id, tag_id=tag_id, trigger_ids=trigger_ids, **update_kwargs)

        # Handle 204 No Content response (successful update with no response body)
        if response is None:
            # For updates that return 204, we need to fetch the updated tag to return the response
            updated_tag = client.tag_manager.get_tag(app_id=app_id, tag_id=tag_id)
            return TagManagerSingleResponse(**updated_tag)

        return TagManagerSingleResponse(**response)
    except NotFoundError:
        raise RuntimeError(f"Tag with ID {tag_id} not found in app {app_id}")
    except BadRequestError as e:
        raise RuntimeError(f"Failed to update tag: {e.message}")
    except Exception as e:
        raise RuntimeError(f"Failed to update tag: {str(e)}")


def delete_tag(app_id: str, tag_id: str) -> OperationStatusResponse:
    try:
        client = create_piwik_client()
        client.tag_manager.delete_tag(app_id, tag_id)
        return OperationStatusResponse(
            status="success",
            message=f"Tag {tag_id} deleted successfully from app {app_id}",
        )
    except NotFoundError:
        raise RuntimeError(f"Tag with ID {tag_id} not found in app {app_id}")
    except BadRequestError as e:
        raise RuntimeError(f"Failed to delete tag: {e.message}")
    except Exception as e:
        raise RuntimeError(f"Failed to delete tag: {str(e)}")


def copy_tag(
    app_id: str,
    tag_id: str,
    target_app_id: str | None = None,
    name: str | None = None,
    with_triggers: bool = False,
) -> CopyResourceResponse:
    try:
        client = create_piwik_client()
        response = client.tag_manager.copy_tag(
            app_id=app_id,
            tag_id=tag_id,
            name=name,
            target_app_id=target_app_id,
            with_triggers=with_triggers,
        )

        if response is None:
            raise RuntimeError("Empty response from API while copying tag")

        data: dict[str, Any] = response.get("data", {})
        relationships: dict[str, Any] = data.get("relationships", {})
        operation = relationships.get("operation", {}).get("data", {})

        return CopyResourceResponse(
            resource_id=data.get("id", ""),
            resource_type=data.get("type", "tag"),
            operation_id=operation.get("id", ""),
            copied_into_app_id=target_app_id or app_id,
            name=name,
            with_triggers=with_triggers,
        )
    except NotFoundError:
        raise RuntimeError(f"Tag with ID {tag_id} not found in app {app_id}")
    except BadRequestError as e:
        raise RuntimeError(f"Failed to copy tag: {e.message}")
    except Exception as e:
        raise RuntimeError(f"Failed to copy tag: {str(e)}")


def register_tag_tools(mcp: FastMCP) -> None:
    """Register all tag management tools with the MCP server."""

    @mcp.tool(annotations={"title": "Piwik PRO: List Tags", "readOnlyHint": True})
    def tags_list(
        app_id: str,
        limit: int = 10,
        offset: int = 0,
        filters: dict[str, Any] | None = None,
    ) -> TagManagerListResponse:
        """List tags for an app in Piwik PRO Tag Manager.

        Args:
            app_id: UUID of the app
            limit: Maximum number of tags to return (default: 10)
            offset: Number of tags to skip (default: 0)
            filters: Filter by tag name, is_active, template, consent_type, is_prioritized, has_any_triggers
        """
        return list_tags(app_id=app_id, limit=limit, offset=offset, filters=filters)

    @mcp.tool(annotations={"title": "Piwik PRO: Get Tag", "readOnlyHint": True})
    def tags_get(app_id: str, tag_id: str) -> TagManagerSingleResponse:
        """Get detailed information about a specific tag.

        Related Tools:
            - tags_list_triggers(app_id, tag_id) - Get triggers attached to this tag
            - variables_list(app_id) - Discover valid variable names used by tag fields
        """
        return get_tag(app_id, tag_id)

    @mcp.tool(annotations={"title": "Piwik PRO: List Triggers for Tag", "readOnlyHint": True})
    def tags_list_triggers(
        app_id: str,
        tag_id: str,
        limit: int | None = None,
        offset: int | None = None,
        sort: str | None = None,
        name: str | None = None,
        trigger_type: str | None = None,
    ) -> dict:
        """Get list of triggers attached to a specific tag.

        Args:
            app_id: UUID of the app
            tag_id: UUID of the tag
            limit: Maximum number of triggers to return
            offset: Number of triggers to skip
            sort: Sort order - 'name', '-name', 'created_at', '-created_at', etc.
            name: Filter by trigger name (partial match)
            trigger_type: Filter by trigger type
        """
        return get_tag_triggers(app_id, tag_id, limit, offset, sort, name, trigger_type)

    @mcp.tool(annotations={"title": "Piwik PRO: Create Tag"})
    def tags_create(app_id: str, attributes: dict, triggers: str = "") -> TagManagerSingleResponse:
        """Create a new tag in Piwik PRO Tag Manager using JSON attributes.

        Before calling this tool, always check both:
        - `templates_get_tag(template_name)` for template-specific requirements, examples,
          and variable-reference guidance
        - `tools_parameters_get("tags_create")` for the runtime JSON schema of the `attributes` object

        Only templates listed by `templates_list_tags()` are supported.

        Required workflow:
            1. templates_list_tags() → get exact template names
            2. templates_get_tag(template_name='...') → get requirements for your chosen template
            3. tags_create() → create the tag with verified template name

        Args:
            triggers: Optional comma-separated trigger UUIDs to attach during creation.
                Use an empty string to create the tag without triggers.
                Use triggers_list() to discover available triggers and their UUIDs.
                Use variables_list() to discover available variables used in trigger conditions.

        Returns:
            Created tag resource. The response may include `data.relationships.unrecognized_variables`
            when the backend detects unresolved variable references.
        """
        return create_tag(app_id, attributes, triggers)

    @mcp.tool(annotations={"title": "Piwik PRO: Update Tag"})
    def tags_update(
        app_id: str, tag_id: str, attributes: dict, triggers: str = "__unchanged__"
    ) -> TagManagerSingleResponse:
        """Update an existing tag using JSON attributes.

        Before calling this tool, always check both:
        - `templates_get_tag(template_name)` for template-specific editable fields, examples,
          and variable-reference guidance
        - `tools_parameters_get("tags_update")` for the runtime JSON schema of the `attributes` object

        Args:
            triggers: Optional comma-separated trigger UUIDs replacing current triggers.
                Use `__unchanged__` to keep triggers as-is.
                Use an empty string to remove all triggers.
        """
        return update_tag(app_id, tag_id, attributes, triggers)

    @mcp.tool(annotations={"title": "Piwik PRO: Delete Tag"})
    def tags_delete(app_id: str, tag_id: str) -> OperationStatusResponse:
        """Delete a tag from Piwik PRO Tag Manager.

        Warning: This action is irreversible.
        """
        return delete_tag(app_id, tag_id)

    @mcp.tool(annotations={"title": "Piwik PRO: Copy Tag"})
    def tags_copy(
        app_id: str,
        tag_id: str,
        target_app_id: str | None = None,
        name: str | None = None,
        with_triggers: bool = False,
    ) -> CopyResourceResponse:
        """Copy a tag, optionally to another app and with triggers.

        Args:
            target_app_id: Optional UUID of the target app. If omitted, copies within the same app.
            with_triggers: Whether to copy triggers attached to the tag (tag-only option)
        """
        return copy_tag(app_id, tag_id, target_app_id, name, with_triggers)
