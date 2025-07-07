"""
Variable management tools for Piwik PRO Tag Manager.

This module provides MCP tools for managing variables, including creation,
updating, listing, and detailed information retrieval.
"""

from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP

from piwik_pro_mcp.api.exceptions import BadRequestError, NotFoundError
from piwik_pro_mcp.api.methods.tag_manager.models import (
    TagManagerListResponse,
    TagManagerSingleResponse,
    VariableFilters,
)

from ...common.templates import list_template_names
from ...common.utils import create_piwik_client, validate_data_against_model
from ...responses import CopyResourceResponse
from .models import VariableCreateAttributes, VariableUpdateAttributes


def list_variables(
    app_id: str,
    limit: int = 10,
    offset: int = 0,
    filters: Optional[Dict[str, Any]] = None,
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
        allowed_variable_types = set(list_template_names("tag_manager/variables"))
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
    target_app_id: Optional[str] = None,
    name: Optional[str] = None,
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

        data: Dict[str, Any] = response.get("data", {})
        relationships: Dict[str, Any] = data.get("relationships", {})
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
        filters: Optional[Dict[str, Any]] = None,
    ) -> TagManagerListResponse:
        """List variables for an app in Piwik PRO Tag Manager.

        Args:
            app_id: UUID of the app
            limit: Maximum number of variables to return (default: 10)
            offset: Number of variables to skip (default: 0)
            filters: Filter by variable name, type, and builtin status

        Returns:
            Dictionary containing variable list and metadata including:
            - data: List of variable objects with id, name, template, and attributes
            - meta: Metadata with pagination information
        """
        return list_variables(
            app_id=app_id,
            limit=limit,
            offset=offset,
            filters=filters,
        )

    @mcp.tool(annotations={"title": "Piwik PRO: Get Variable", "readOnlyHint": True})
    def variables_get(app_id: str, variable_id: str) -> TagManagerSingleResponse:
        """Get detailed information about a specific variable.

        Args:
            app_id: UUID of the app
            variable_id: UUID of the variable

        Returns:
            Dictionary containing variable details including:
            - data: Variable object with id, name, template, and all attributes
            - Variable configuration and value settings
        """
        return get_variable(app_id, variable_id)

    @mcp.tool(annotations={"title": "Piwik PRO: Create Variable"})
    def variables_create(app_id: str, attributes: dict) -> TagManagerSingleResponse:
        """Create a new variable in Piwik PRO Tag Manager using JSON attributes.

        Only variable types listed by `templates_list_variables()` are supported. Any other type will be refused.

        This tool uses a simplified interface with 2 parameters: app_id and attributes.
        Use tools_parameters_get("variables_create") to get the complete JSON schema
        with all available fields, types, and validation rules.

        💡 TIP: Use these tools to discover available templates and their requirements:
        - templates_list_variables() - List all available variable templates
        - templates_get_variable(template_name='data_layer') - Get complete template info with field mutability

        Args:
            app_id: UUID of the app
            attributes: Dictionary containing variable attributes for creation. Required fields are
                       'name' and 'variable_type'. Field 'is_active' is optional.

        Returns:
            Dictionary containing created variable information including:
            - data: Created variable object with id, name, template, and attributes
            - Variable configuration and value settings

        Parameter Discovery:
            Use tools_parameters_get("variables_create") to get the complete JSON schema
            for all available fields. This returns validation rules, field types, and examples.

        Template Discovery:
            Use piwik_get_available_variable_templates() to see all available templates, then
            use piwik_get_variable_template(template_name) for detailed template information.

        Examples:
            # Get available parameters first
            schema = tools_parameters_get("variables_create")

            # Discover available templates
            templates = templates_list_variables()
            template_info = templates_get_variable(template_name='data_layer')

            # Create data layer variable
            attributes = {
                "name": "Order Total",
                "variable_type": "data_layer",
                "data_layer_variable_name": "ecommerce.purchase.value",
                "default_value": "0"
            }

            # Create custom JavaScript variable
            attributes = {
                "name": "User Status",
                "variable_type": "custom_javascript",
                "value": "return localStorage.getItem('userId') ? 'logged_in' : 'guest';"
            }
        """
        return create_variable(app_id, attributes)

    @mcp.tool(annotations={"title": "Piwik PRO: Update Variable"})
    def variables_update(app_id: str, variable_id: str, attributes: dict) -> TagManagerSingleResponse:
        """Update an existing variable in Piwik PRO Tag Manager using JSON attributes.

        This tool updates only editable fields and automatically filters out create-only and read-only fields.
        Use the variable template tools to understand field mutability before updating.

        💡 TIP: Use these tools to understand field mutability and available options:
        - templates_list_variables() - List all available variable templates
        - templates_get_variable(template_name) - Get detailed field mutability information

        Args:
            app_id: UUID of the app
            variable_id: UUID of the variable to update
            attributes: Dictionary containing variable attributes to update. Only editable fields will be processed.
                       Create-only fields (variable_type) will be ignored.
                       Read-only fields (created_at, updated_at) will be filtered out automatically.

        Returns:
            Dictionary containing updated variable information including:
            - data: Updated variable object with id, name, template, and attributes
            - Variable configuration and updated settings

        Field Mutability:
            ✅ Editable: name, is_active, template-specific options (can be updated anytime)
            ⚠️ Create-only: variable_type (ignored in updates)
            🚫 Read-only: created_at, updated_at (filtered out automatically)

        Examples:
            # Get template information to understand editable fields
            template_info = templates_get_variable(template_name='data_layer')

            # Update variable name and settings
            attributes = {
                "name": "Updated Order Total",
                "is_active": True,
                "data_layer_variable_name": "ecommerce.transaction_value",
                "default_value": "0.00"
            }

            # Update custom JavaScript variable code
            attributes = {
                "name": "Enhanced User Status",
                "value": "return localStorage.getItem('userId') ? 'premium' : 'free';"
            }

        Parameter Discovery:
            Use tools_parameters_get("variables_update") to get the complete JSON schema
            for all available fields, then consult the variable template for mutability information.
        """
        return update_variable(app_id, variable_id, attributes)

    @mcp.tool(annotations={"title": "Piwik PRO: Copy Variable"})
    def variables_copy(
        app_id: str,
        variable_id: str,
        target_app_id: Optional[str] = None,
        name: Optional[str] = None,
    ) -> CopyResourceResponse:
        """Copy a variable, optionally to another app.

        Args:
            app_id: UUID of the source app
            variable_id: UUID of the variable to copy
            target_app_id: Optional UUID of the target app. If omitted, copies within the same app.
            name: Optional new name for the copied variable

        Returns:
            Normalized copy response including new resource id and operation id.
        """
        return copy_variable(app_id, variable_id, target_app_id, name)
