"""
CDP (Customer Data Platform) management MCP tools.

This module provides MCP tool functions for managing Piwik PRO audiences,
including creation, listing, and retrieval of audiences.
"""

from mcp.server.fastmcp import FastMCP

from piwik_pro_mcp.responses import OperationStatusResponse

from .attributes import list_cdp_attributes as _list_cdp_attributes
from .audiences import (
    create_audience as _create_audience,
)
from .audiences import (
    delete_audience as _delete_audience,
)
from .audiences import (
    get_audience_details as _get_audience_details,
)
from .audiences import (
    list_audiences as _list_audiences,
)
from .audiences import (
    update_audience as _update_audience,
)
from .models import (
    AttributeListMCPResponse,
    AudienceCreateMCPResponse,
    AudienceDetailsMCPResponse,
    AudienceListMCPResponse,
    AudienceUpdateMCPResponse,
)


def register_cdp_tools(mcp: FastMCP) -> None:
    """Register all CDP management tools with the MCP server."""

    @mcp.tool("audiences_list", annotations={"title": "Piwik PRO: List Audiences", "readOnlyHint": True})
    def audiences_list(app_id: str) -> AudienceListMCPResponse:
        """List audiences from Piwik PRO CDP.

        Retrieves a list of audiences that are configured in the Piwik PRO
        Customer Data Platform for the specified app.

        Args:
            app_id: UUID of the app to list audiences for

        Returns:
            Dictionary containing audience list including:
            - audiences: List of audience objects with id, name, description, etc.
            - total: Total number of audiences available
        """
        return _list_audiences(app_id=app_id)

    @mcp.tool("audiences_get", annotations={"title": "Piwik PRO: Get Audience", "readOnlyHint": True})
    def audiences_get(app_id: str, audience_id: str) -> AudienceDetailsMCPResponse:
        """Get detailed information about a specific audience.

        Args:
            app_id: UUID of the app
            audience_id: UUID of the audience to retrieve

        Returns:
            Dictionary containing detailed audience information including:
            - id: Audience UUID
            - name: Audience name
            - description: Audience description
            - membership_duration_days: Duration in days for audience membership
            - version: Audience version
            - definition: Audience definition with conditions
            - author_email: Email of the audience author
            - is_author: Whether current user is the author
            - created_at: Audience creation datetime
            - updated_at: Audience last update datetime
        """
        return _get_audience_details(app_id=app_id, audience_id=audience_id)

    @mcp.tool("audiences_create", annotations={"title": "Piwik PRO: Create Audience"})
    def audiences_create(app_id: str, attributes: dict) -> AudienceCreateMCPResponse:
        """Create a new audience in Piwik PRO CDP using JSON attributes.

        ⚠️  IMPORTANT: Before creating audiences
        * First discover available parameters using list_available_parameters("audiences_create") tool.
        * Only then use activations_attributes_list() to get the correct column_id, value_selectors, and value_format.

        Args:
            app_id: UUID of the app to create audience for
            attributes: Dictionary containing audience attributes for creation.
                        Required fields are 'name', 'description', 'definition', and 'membership_duration_days'.


        Returns:
            Dictionary containing created audience information including:
            - status: Creation status ("success" or "error")
            - message: Descriptive message about the creation
            - audience_id: ID of the created audience (if available)
            - audience_name: Name of the created audience

        Examples:
            # STEP 1: Discover available attributes
            attrs = activations_attributes_list("your-app-id")
            # STEP 2: Create audience with discovered attribute
            attributes = {
                "name": "US Users",
                "description": "Users from United States",
                "definition": {
                    "operator": "and",
                    "conditions": [{
                        "operator": "or",
                        "conditions": [{
                            "condition_type": "profile",
                            "column_id": location_attr.column_id,  # Use discovered column_id
                            "value_selector": location_attr.value_selectors[0],  # Use supported selector
                            "condition": {"operator": "eq", "value": "US"}
                        }]
                    }]
                },
                "membership_duration_days": 30
            }

            # Example with datetime attribute (after discovering last_activity_time)
            attributes = {
                "name": "Recent Users",
                "description": "Users active after Dec 31, 2024",
                "definition": {
                    "operator": "and",
                    "conditions": [{
                        "operator": "or",
                        "conditions": [{
                            "condition_type": "profile",
                            "column_id": "last_activity_time",  # From attribute discovery
                            "value_selector": "none",
                            "condition": {
                                "operator": "later_than",  # Supported for datetime type
                                "value": {"value": "2024-12-31T23:59:59Z", "unit": "datetime"}  # CORRECT FORMAT!
                            }
                        }]
                    }]
                },
                "membership_duration_days": 520
            }

            # Example with event condition (behavioral targeting)
            attributes = {
                "name": "Frequent Purchasers",
                "description": "Users who made more than 3 purchases in the last 30 days",
                "definition": {
                    "operator": "and",
                    "conditions": [{
                        "operator": "or",
                        "conditions": [{
                            "condition_type": "event",
                            "times": {
                                "operator": "gt",
                                "value": 3
                            },
                            "during": {  # Optional: time window
                                "seconds": 2592000,  # 30 days in seconds
                                "unit": "days"
                            },
                            "condition": {
                                "operator": "and",
                                "conditions": [{
                                    "column_id": "event_type",  # From attribute discovery
                                    "condition": {
                                        "operator": "eq",
                                        "value": 2  # Purchase event type
                                    }
                                }]
                            }
                        }]
                    }]
                },
                "membership_duration_days": 30
            }

        TIP: Always use list_available_parameters("audiences_create") first to discover available parameters.
        TIP: Always use activations_attributes_list() first to discover available attributes and their formats.
        TIP: Use the supported_operators field from attribute discovery to know which operators work.
        TIP: Use the value_format.example from each attribute for correct value formatting.
        TIP: Profile attributes with value_selectors require a value_selector field in conditions.
        TIP: Event attributes never use value_selectors - use them directly in event conditions.
        """
        return _create_audience(app_id=app_id, attributes=attributes)

    @mcp.tool("audiences_update", annotations={"title": "Piwik PRO: Update Audience"})
    def audiences_update(app_id: str, audience_id: str, attributes: dict) -> AudienceUpdateMCPResponse:
        """Update an existing audience in Piwik PRO CDP using JSON attributes.

        ⚠️  IMPORTANT: Before updating audiences
        * First discover available parameters using list_available_parameters("audiences_update") tool.
        * Only then use activations_attributes_list() to get the correct column_id, value_selectors,
            and value_format for new conditions.

        NOTE: While the underlying API requires all fields, you can provide only the fields you want to change.
        The tool will automatically fetch current values and merge them with your updates.

        Args:
            app_id: UUID of the app containing the audience
            audience_id: UUID of the audience to update
            attributes: Dictionary containing audience attributes to update.
                        You can provide any combination of:
                            'name', 'description', 'definition', 'membership_duration_days'.
                        Only the fields you provide will be updated - other fields keep their current values.

        Returns:
            Dictionary containing update status and information including:
            - status: Update status ("success" or "error")
            - message: Descriptive message about the update
            - audience_id: ID of the updated audience
            - audience_name: Name of the updated audience
            - updated_fields: List of fields that were modified

        Examples:
            # Update just the name and description
            attributes = {
                "name": "High Value Inactive Customers - Updated",
                "description": "Updated description for high-value customers who haven't engaged recently"
            }

            # Update just the definition (add new conditions)
            attributes = {
                "definition": {
                    "operator": "and",
                    "conditions": [{
                        "operator": "or",
                        "conditions": [{
                            "condition_type": "profile",
                            "column_id": "total_revenue",
                            "value_selector": "none",
                            "condition": {"operator": "gte", "value": 1000}  # Changed threshold
                        }]
                    }]
                }
            }

            # Update membership duration only
            attributes = {
                "membership_duration_days": 120  # Changed from previous value
            }

        TIP: Always use list_available_parameters("audiences_update") first to discover available parameters.
        TIP: For definition updates, use activations_attributes_list() to get correct attribute formats.
        TIP: Use the supported_operators field from attribute discovery to know which operators work.
        TIP: Profile attributes with value_selectors require a value_selector field in conditions.
        """
        return _update_audience(app_id=app_id, audience_id=audience_id, attributes=attributes)

    @mcp.tool("audiences_delete", annotations={"title": "Piwik PRO: Delete Audience"})
    def audiences_delete(app_id: str, audience_id: str) -> OperationStatusResponse:
        """Delete an existing audience in Piwik PRO CDP.

        ⚠️  WARNING: This operation is irreversible! The audience and all its data will be permanently deleted.

        Args:
            app_id: UUID of the app containing the audience
            audience_id: UUID of the audience to delete

        Returns:
            Dictionary containing deletion status and information including:
            - status: Deletion status ("success" or "error")
            - message: Descriptive message about the deletion

        Examples:
            # Delete an audience
            result = audiences_delete("07b417fb-1d68-4ea5-9f89-44aece1423ea", "audience-123")
        """
        return _delete_audience(app_id=app_id, audience_id=audience_id)

    @mcp.tool(
        "activations_attributes_list", annotations={"title": "Piwik PRO: List CDP Attributes", "readOnlyHint": True}
    )
    def activations_attributes_list(app_id: str) -> AttributeListMCPResponse:
        """List all CDP attributes available for audience creation.

        This tool returns structured attribute objects containing all available attributes
        for the specified app. Each AttributeSummary object includes:
        - column_id: Unique identifier for the attribute
        - column_name: Human-readable name
        - column_type: Data type (string, number, datetime, etc.)
        - supported_operators: List of operators valid for this column type
        - value_selectors: Supported selectors (first, last, any, none)
        - value_format: CRITICAL - Format requirements and examples for condition values
        - column_category: Categories the attribute belongs to
        - scope: Whether it's an event or profile attribute
        - immutable: Whether the attribute is read-only
        - event_data_key: Key for imported data or tracker dimension

        This information is essential for creating audience conditions with correct
        column_id, operators, value_selectors, and most importantly - correct value formats.

        Args:
            app_id: UUID of the app to list attributes for

        Returns:
            AttributeListMCPResponse containing:
            - attributes: List of AttributeSummary objects with structured metadata
            - total: Total number of attributes available
        """
        return _list_cdp_attributes(app_id=app_id)
