"""
Variable management tools for Piwik PRO Tag Manager.

This module provides MCP tools for managing variables, including creation,
updating, listing, and detailed information retrieval.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP

from piwik_pro_mcp.api.exceptions import BadRequestError, NotFoundError
from piwik_pro_mcp.api.methods.tag_manager.models import (
    TagManagerListResponse,
    TagManagerSingleResponse,
    VariableFilters,
)

from ...common.templates import list_available_assets
from ...common.utils import create_piwik_client, validate_data_against_model
from ...responses import CopyResourceResponse
from .models import VariableCreateAttributes, VariableUpdateAttributes


def list_variables(
    app_id: str,
    limit: int = 10,
    offset: int = 0,
    filters: dict[str, Any] | None = None,
) -> TagManagerListResponse:
    if filters is not None:
        filters = validate_data_against_model(filters, VariableFilters, invalid_item_label="filter")
    try:
        client = create_piwik_client()
        response = client.tag_manager.list_variables(
            app_id=app_id,
            limit=limit,
            offset=offset,
            filters=filters,
        )
        return TagManagerListResponse(**response)
    except Exception as e:
        raise RuntimeError(f"Failed to list variables: {str(e)}")


def get_variable(app_id: str, variable_id: str) -> TagManagerSingleResponse:
    try:
        client = create_piwik_client()
        response = client.tag_manager.get_variable(app_id, variable_id)
        return TagManagerSingleResponse(**response)
    except NotFoundError:
        raise RuntimeError(f"Variable with ID {variable_id} not found in app {app_id}")
    except Exception as e:
        raise RuntimeError(f"Failed to get variable: {str(e)}")


def create_variable(app_id: str, attributes: dict) -> TagManagerSingleResponse:
    try:
        client = create_piwik_client()

        # Validate attributes directly against the variable create model
        validated_attrs = validate_data_against_model(attributes, VariableCreateAttributes)

        # Convert to dictionary and filter out None values
        create_kwargs = {k: v for k, v in validated_attrs.model_dump(exclude_none=True).items()}

        # Extract required fields
        name = create_kwargs.pop("name")
        variable_type = create_kwargs.pop("variable_type")

        # Enforce assets-driven allowlist via model validation (retained as a safety check)
        allowed_variable_types = set(list_available_assets("tag_manager/variables").keys())
        if variable_type not in allowed_variable_types:
            raise RuntimeError(
                f"Unsupported variable type '{variable_type}'. Use templates_list_variables() to discover options."
            )

        response = client.tag_manager.create_variable(
            app_id=app_id, name=name, variable_type=variable_type, **create_kwargs
        )
        return TagManagerSingleResponse(**response)
    except BadRequestError as e:
        raise RuntimeError(
            f"Failed to create variable: API request failed (HTTP {e.status_code}): {e.message}. "
            f"Full response: {e.response_data}"
        )
    except Exception as e:
        raise RuntimeError(f"Failed to create variable: {str(e)}")


def update_variable(app_id: str, variable_id: str, attributes: dict) -> TagManagerSingleResponse:
    try:
        client = create_piwik_client()

        # Validate attributes against the variable update model
        validated_attrs = validate_data_against_model(attributes, VariableUpdateAttributes)

        # Convert to dictionary and filter out None values
        # Use by_alias=True to match API layer expectations
        update_kwargs = {k: v for k, v in validated_attrs.model_dump(by_alias=True, exclude_none=True).items()}

        if not update_kwargs:
            raise RuntimeError("No editable fields provided for update")

        response = client.tag_manager.update_variable(app_id=app_id, variable_id=variable_id, **update_kwargs)

        # Handle 204 No Content response (successful update with no response body)
        if response is None:
            # For updates that return 204, we need to fetch the updated variable to return the response
            updated_variable = client.tag_manager.get_variable(app_id=app_id, variable_id=variable_id)
            return TagManagerSingleResponse(**updated_variable)

        return TagManagerSingleResponse(**response)

    except NotFoundError:
        raise RuntimeError(f"Variable with ID {variable_id} not found in app {app_id}")
    except BadRequestError as e:
        raise RuntimeError(f"Failed to update variable: {e.message}")
    except Exception as e:
        raise RuntimeError(f"Failed to update variable: {str(e)}")


def copy_variable(
    app_id: str,
    variable_id: str,
    target_app_id: str | None = None,
    name: str | None = None,
) -> CopyResourceResponse:
    try:
        client = create_piwik_client()
        response = client.tag_manager.copy_variable(
            app_id=app_id,
            variable_id=variable_id,
            name=name,
            target_app_id=target_app_id,
        )

        if response is None:
            raise RuntimeError("Empty response from API while copying variable")

        data: dict[str, Any] = response.get("data", {})
        relationships: dict[str, Any] = data.get("relationships", {})
        operation = relationships.get("operation", {}).get("data", {})

        resp_name = name
        if "attributes" in data and isinstance(data["attributes"], dict):
            resp_name = data["attributes"].get("name", name)

        return CopyResourceResponse(
            resource_id=data.get("id", ""),
            resource_type=data.get("type", "variable"),
            operation_id=operation.get("id", ""),
            copied_into_app_id=target_app_id or app_id,
            name=resp_name,
        )
    except NotFoundError:
        raise RuntimeError(f"Variable with ID {variable_id} not found in app {app_id}")
    except BadRequestError as e:
        raise RuntimeError(f"Failed to copy variable: {e.message}")
    except Exception as e:
        raise RuntimeError(f"Failed to copy variable: {str(e)}")


def register_variable_tools(mcp: FastMCP) -> None:
    """Register all variable management tools with the MCP server."""

    @mcp.tool(annotations={"title": "Piwik PRO: List Variables", "readOnlyHint": True})
    def variables_list(
        app_id: str,
        limit: int = 10,
        offset: int = 0,
        filters: dict[str, Any] | None = None,
    ) -> TagManagerListResponse:
        """List variables for an app in Piwik PRO Tag Manager.

        Args:
            app_id: UUID of the app
            limit: Maximum number of variables to return (default: 10)
            offset: Number of variables to skip (default: 0)
            filters: Optional filter keys: `name`, `variable_type`, and `builtin`
        """
        return list_variables(
            app_id=app_id,
            limit=limit,
            offset=offset,
            filters=filters,
        )

    @mcp.tool(annotations={"title": "Piwik PRO: Get Variable", "readOnlyHint": True})
    def variables_get(app_id: str, variable_id: str) -> TagManagerSingleResponse:
        """Get detailed information about a specific variable."""
        return get_variable(app_id, variable_id)

    @mcp.tool(annotations={"title": "Piwik PRO: Create Variable"})
    def variables_create(app_id: str, attributes: dict) -> TagManagerSingleResponse:
        """Create a new variable in Piwik PRO Tag Manager using JSON attributes.

        Before calling this tool, always check both:
        - `templates_list_variables()` and `templates_get_variable(template_name)` for variable type requirements
        - `tools_parameters_get("variables_create")` for the runtime JSON schema of the `attributes` object

        Only variable types listed by `templates_list_variables()` are supported.

        Required workflow:
            1. templates_list_variables() → get exact variable type names
            2. templates_get_variable(template_name='...') → get requirements for your chosen type
            3. variables_create() → create the variable with verified type name
        """
        return create_variable(app_id, attributes)

    @mcp.tool(annotations={"title": "Piwik PRO: Update Variable"})
    def variables_update(app_id: str, variable_id: str, attributes: dict) -> TagManagerSingleResponse:
        """Update an existing variable in Piwik PRO Tag Manager using JSON attributes.

        Only editable fields are processed — create-only fields (variable_type) are ignored,
        read-only fields (created_at, updated_at) are filtered out automatically.

        Use templates_get_variable(template_name) to understand field mutability before updating.
        Use tools_parameters_get("variables_update") to get the complete JSON schema.
        """
        return update_variable(app_id, variable_id, attributes)

    @mcp.tool(annotations={"title": "Piwik PRO: Copy Variable"})
    def variables_copy(
        app_id: str,
        variable_id: str,
        target_app_id: str | None = None,
        name: str | None = None,
    ) -> CopyResourceResponse:
        """Copy a variable, optionally to another app.

        Args:
            target_app_id: Optional UUID of the target app. If omitted, copies within the same app.
        """
        return copy_variable(app_id, variable_id, target_app_id, name)
