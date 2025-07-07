"""
Tag management tools for Piwik PRO Tag Manager.

This module provides MCP tools for managing tags, including creation,
updating, listing, deletion, and relationship management with triggers.
"""

from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP

from piwik_pro_mcp.api.exceptions import BadRequestError, NotFoundError
from piwik_pro_mcp.api.methods.tag_manager.models import TagFilters, TagManagerListResponse, TagManagerSingleResponse

from ...common.templates import list_template_names
from ...common.utils import create_piwik_client, validate_data_against_model
from ...responses import CopyResourceResponse, OperationStatusResponse
from .models import TagManagerCreateAttributes, TagManagerUpdateAttributes


def list_tags(
    app_id: str,
    limit: int = 10,
    offset: int = 0,
    filters: Optional[Dict[str, Any]] = None,
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
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    sort: Optional[str] = None,
    name: Optional[str] = None,
    trigger_type: Optional[str] = None,
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
        allowed_templates = set(list_template_names("tag_manager/tags"))
        if template not in allowed_templates:
            raise RuntimeError(f"Unsupported tag template '{template}'. Use templates_list() to discover options.")

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
    target_app_id: Optional[str] = None,
    name: Optional[str] = None,
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

        data: Dict[str, Any] = response.get("data", {})
        relationships: Dict[str, Any] = data.get("relationships", {})
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
    @mcp.tool(annotations={"title": "Piwik PRO: List Tags", "readOnlyHint": True})
    def tags_list(
        app_id: str,
        limit: int = 10,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None,
    ) -> TagManagerListResponse:
        """List tags for an app in Piwik PRO Tag Manager.

        Args:
            app_id: UUID of the app
            limit: Maximum number of tags to return (default: 10)
            offset: Number of tags to skip (default: 0)
            filters: Filter by tag name, is_active, template, consent_type, is_prioritized, has_any_triggers, tag_type

        Returns:
            Dictionary containing tag list and metadata including:
            - data: List of tag objects with id, name, template, and attributes
            - meta: Metadata with pagination information
        """
        return list_tags(app_id=app_id, limit=limit, offset=offset, filters=filters)

    @mcp.tool(annotations={"title": "Piwik PRO: Get Tag", "readOnlyHint": True})
    def tags_get(app_id: str, tag_id: str) -> TagManagerSingleResponse:
        """Get detailed information about a specific tag.

        Args:
            app_id: UUID of the app
            tag_id: UUID of the tag

        Returns:
            Dictionary containing tag details including:
            - data: Tag object with id, name, template, and all attributes
            - Tag configuration and settings

        Related Tools:
            - tags_list_triggers(app_id, tag_id) - Get triggers attached to this tag
            - templates_get_tag(template_name) - Get template info for tag's template
            - tags_update(app_id, tag_id, attributes) - Update this tag
        """
        return get_tag(app_id, tag_id)

    @mcp.tool(annotations={"title": "Piwik PRO: List Triggers for Tag", "readOnlyHint": True})
    def tags_list_triggers(
        app_id: str,
        tag_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        name: Optional[str] = None,
        trigger_type: Optional[str] = None,
    ) -> dict:
        """Get list of triggers attached to a specific tag.

        This tool helps you understand what triggers are configured to fire a specific tag,
        which is essential for debugging and managing tag behavior.

        Args:
            app_id: UUID of the app
            tag_id: UUID of the tag to get triggers for
            limit: Maximum number of triggers to return (optional)
            offset: Number of triggers to skip for pagination (optional)
            sort: Sort order - 'name', '-name', 'created_at', '-created_at', etc. (optional)
            name: Filter by trigger name (partial match, optional)
            trigger_type: Filter by trigger type like 'page_view', 'click', 'custom_event' (optional)

        Returns:
            Dictionary containing list of triggers attached to the tag including:
            - data: Array of trigger objects with id, type, and attributes
            - meta: Pagination metadata with total count
            - links: Pagination links for navigation

        Examples:
            # Get all triggers for a tag
            tags_list_triggers("app-id", "tag-id")

            # Get triggers with pagination
            tags_list_triggers("app-id", "tag-id", limit=10, offset=0)

            # Filter by trigger type
            tags_list_triggers("app-id", "tag-id", trigger_type="click")

            # Sort by name descending
            tags_list_triggers("app-id", "tag-id", sort="-name")

        Use Cases:
            - Debug why a tag is not firing (check if triggers are attached)
            - Understand tag behavior by seeing all its triggers
            - Audit tag configuration for compliance or optimization
            - Manage trigger-tag relationships in complex setups
        """
        return get_tag_triggers(app_id, tag_id, limit, offset, sort, name, trigger_type)

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
            piwik_get_trigger_tags(
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

    @mcp.tool(annotations={"title": "Piwik PRO: Create Tag"})
    def tags_create(app_id: str, attributes: dict, triggers: str = "") -> TagManagerSingleResponse:
        """Create a new tag in Piwik PRO Tag Manager using JSON attributes.

        Only templates listed by `templates_list()` are supported. Any other template will be refused.

        💡 TIP: Use these tools to discover available templates and their requirements:
        - templates_list() - List all available templates
        - templates_get_tag(template_name='custom_tag') - Get detailed requirements

        This tool uses a simplified interface with 3 parameters: app_id, attributes, and triggers.
        Use tools_parameters_get("tags_create") to get the complete JSON schema
        with all available fields, types, and validation rules.

        Args:
            app_id: UUID of the app
            attributes: Dictionary containing tag attributes for creation. Required fields vary by template:
                       - name: Tag name (always required)
                       - template: Template type (use piwik_get_tag_template() to see options)
                       - consent_type: Consent type (e.g., 'not_require_consent', 'analytics')
                       - Additional required fields depend on the template
            triggers: Comma-separated list of trigger UUIDs to attach to this tag (optional)
                     e.g., "trigger-uuid-1,trigger-uuid-2" or "trigger-uuid-1"

        Returns:
            Dictionary containing created tag information including:
            - data: Created tag object with id, name, template, and attributes
            - Tag configuration details

        Template Discovery:
            Use piwik_get_available_templates() to see all available templates, or
            piwik_get_tag_template(template_name='TEMPLATE') for specific requirements.

        Trigger Management:
            - Use triggers_list() to discover available triggers
            - Use triggers_get() to understand trigger conditions
            - Use tags_list_triggers() after creation to verify relationships

        Parameter Discovery:
            Use tools_parameters_get("tags_create") to get the complete JSON schema
            for all available fields. This returns validation rules, field types, and examples.

        Examples:
            # Get available templates first
            templates = templates_list()

            # Get specific template requirements
            piwik_info = templates_get_tag(template_name='piwik')

            # Create custom tag
            attributes = {
                "name": "My Custom Tag",
                "template": "custom_tag",
                "consent_type": "not_require_consent",
                "code": "<script>console.log('Hello World');</script>"
            }

            # Create tag with triggers attached
            tags_create(app_id, attributes, triggers="trigger-uuid-1,trigger-uuid-2")

            # Create Piwik PRO analytics tag
            attributes = {
                "name": "Piwik Analytics",
                "template": "piwik",
                "consent_type": "analytics",
                "template_options": {
                    "track_page_view": True,
                    "link_tracking": True
                }
            }
        """
        return create_tag(app_id, attributes, triggers)

    @mcp.tool(annotations={"title": "Piwik PRO: Update Tag"})
    def tags_update(
        app_id: str, tag_id: str, attributes: dict, triggers: str = "__unchanged__"
    ) -> TagManagerSingleResponse:
        """Update an existing tag using JSON attributes.

        This tool uses a simplified interface with 4 parameters: app_id, tag_id, attributes, and triggers.
        Use tools_parameters_get("tags_update") to get the complete JSON schema
        with all available fields, types, and validation rules.

        Args:
            app_id: UUID of the app
            tag_id: UUID of the tag
            attributes: Dictionary containing tag attributes to update. All fields are optional.
                      Supported fields include name, template, and is_active.
            triggers: Comma-separated list of trigger UUIDs to attach to this tag (optional)
                     If provided, replaces all existing triggers. If not provided, existing triggers remain unchanged.
                     Use empty string to remove all triggers.
                     e.g., "trigger-uuid-1,trigger-uuid-2" or "trigger-uuid-1"

        Returns:
            Dictionary containing updated tag information including:
            - data: Updated tag object with all current attributes
            - Updated configuration details

        Trigger Management:
            - Use triggers_list() to discover available triggers
            - Use tags_list_triggers() to see current trigger relationships
            - Use triggers_list_tags() to understand trigger impact
            - Don't pass triggers parameter to leave existing triggers unchanged
            - Pass empty string to triggers parameter to remove all triggers

        Parameter Discovery:
            Use tools_parameters_get("tags_update") to get the complete JSON schema
            for all available fields. This returns validation rules, field types, and examples.

        Examples:
            # Get available parameters first
            schema = tools_parameters_get("tags_update")

            # Update tag name only (existing triggers remain unchanged)
            attributes = {"name": "Updated Tag Name"}

            # Update tag and set triggers
            tags_update(app_id, tag_id, {"name": "New Name"}, triggers="trigger-uuid-1,trigger-uuid-2")

            # Remove all triggers from a tag
            tags_update(app_id, tag_id, {}, triggers="")

            # Update multiple fields
            attributes = {
                "name": "Updated Tag",
                "is_active": False
            }
        """
        return update_tag(app_id, tag_id, attributes, triggers)

    @mcp.tool(annotations={"title": "Piwik PRO: Delete Tag"})
    def tags_delete(app_id: str, tag_id: str) -> OperationStatusResponse:
        """Delete a tag from Piwik PRO Tag Manager.

        Warning: This action is irreversible and will permanently delete the tag.

        Args:
            app_id: UUID of the app
            tag_id: UUID of the tag

        Returns:
            Dictionary containing deletion status:
            - status: "success" if deletion was successful
            - message: Descriptive message about the deletion
        """
        return delete_tag(app_id, tag_id)

    @mcp.tool(annotations={"title": "Piwik PRO: Copy Tag"})
    def tags_copy(
        app_id: str,
        tag_id: str,
        target_app_id: Optional[str] = None,
        name: Optional[str] = None,
        with_triggers: bool = False,
    ) -> CopyResourceResponse:
        """Copy a tag, optionally to another app and with triggers.

        Args:
            app_id: UUID of the source app
            tag_id: UUID of the tag to copy
            target_app_id: Optional UUID of the target app. If omitted, copies within the same app.
            name: Optional new name for the copied tag
            with_triggers: Whether to copy triggers attached to the tag (tag-only option)

        Returns:
            Normalized copy response including new resource id and operation id.
        """
        return copy_tag(app_id, tag_id, target_app_id, name, with_triggers)
