"""
Analytics custom dimensions tools with attributes-based interface.

This module provides MCP tools for managing both standard custom dimensions
(session/event scoped) and product custom dimensions through a unified interface
that uses scope-specific attributes dictionaries.
"""

from typing import Any, Dict, Literal, Optional, Union

from mcp.server.fastmcp import FastMCP

from ...api.exceptions import PiwikProAPIError
from ...common import create_piwik_client
from .models import (
    CustomDimensionItem,
    CustomDimensionsList,
    CustomDimensionSlotsInfo,
    ProductCustomDimensionItem,
    ProductCustomDimensionsList,
    UnifiedCustomDimensionsList,
)
from .validators import (
    ProductDimensionAttrs,
    ProductDimensionUpdateAttrs,
    StandardDimensionAttrs,
    StandardDimensionUpdateAttrs,
)


def register_custom_dimensions_tools(mcp: FastMCP) -> None:  # noqa: PLR0915
    """Register Analytics custom dimensions tools with the MCP server."""

    @mcp.tool(annotations={"title": "Piwik PRO: Create Custom Dimension"})
    def analytics_custom_dimensions_create(
        website_id: str,
        name: str,
        scope: Literal["session", "event", "product"],
        attributes: Dict[str, Any],
        description: Optional[str] = None,
    ) -> Union[CustomDimensionItem, ProductCustomDimensionItem]:
        """
        Create a custom dimension with scope-specific configuration.

        ═══════════════════════════════════════════════════════════════
        COMMON PARAMETERS (all dimension types)
        ═══════════════════════════════════════════════════════════════

        • website_id (str): Website/App UUID
        • name (str): Dimension name displayed in analytics UI
        • scope (str): Dimension type - "session", "event", or "product"
        • description (str, optional): Description (max 300 chars)

        ═══════════════════════════════════════════════════════════════
        SCOPE-SPECIFIC ATTRIBUTES
        ═══════════════════════════════════════════════════════════════

        ┌─────────────────────────────────────────────────────────────┐
        │ For scope="session" or scope="event"                        │
        │ (Standard custom dimensions for visitor/event tracking)     │
        └─────────────────────────────────────────────────────────────┘

        Required attributes:
          • active (bool)
              Whether dimension actively collects data

          • case_sensitive (bool)
              Whether dimension values are case-sensitive
              (e.g., "User" vs "user" treated as same/different)

        Optional attributes:
          • slot (int, min=1)
              Slot number. Auto-assigned by API if not provided.
              Cannot be changed after creation.

          • extractions (list of objects)
              Rules to automatically extract values from page data.
              Each extraction has:
                - target (str): "page_title_regex" | "page_url_regex" | "page_query_parameter"
                - pattern (str): Regex pattern or query param name

        Example attributes:
        ```json
        {
          "active": true,
          "case_sensitive": false,
          "slot": 5,
          "extractions": [
            {
              "target": "page_query_parameter",
              "pattern": "utm_campaign"
            },
            {
              "target": "page_url_regex",
              "pattern": "/products/(.*?)/"
            }
          ]
        }
        ```

        ┌─────────────────────────────────────────────────────────────┐
        │ For scope="product"                                         │
        │ (Product custom dimensions for e-commerce tracking)         │
        └─────────────────────────────────────────────────────────────┘

        Optional attributes:
          • slot (int, min=1)
              Slot number. Auto-assigned by API if not provided.
              Cannot be changed after creation.

        Example attributes:
        ```json
        {
          "slot": 1
        }
        ```

        ═══════════════════════════════════════════════════════════════
        EXTRACTION PATTERNS - TROUBLESHOOTING
        ═══════════════════════════════════════════════════════════════

        ⚠️  Common Issues with Extraction Patterns:

        Problem: "Pattern must contain at least one capture group"
        Solution: For regex targets, wrap the part you want to capture in ()

          ✗ WRONG:  ".*/something.*"     (no capture group)
          ✓ RIGHT:  ".*/something/(.*)"  (captures after /something/)

        Problem: Pattern validation fails before API call
        Solution: This is GOOD - it means the validator caught an invalid pattern
                 early. Read the error message for examples of valid patterns.

        Problem: Pattern works in create but fails in update (or vice versa)
        Solution: Try this two-step workflow:
                 1. Create dimension WITHOUT extractions first
                 2. Update dimension to ADD extractions
                 Some complex patterns may have different validation rules.

        💡 Best Practices:
          • Test regex patterns at regex101.com before using them
          • Use non-greedy captures (.*?) instead of greedy (.*) when possible
          • For query params, use exact param name (no regex needed)
          • Remember: only the FIRST capture group is used as the dimension value

        ═══════════════════════════════════════════════════════════════
        EXAMPLES
        ═══════════════════════════════════════════════════════════════

        Create session dimension with auto-extraction:
        ```python
        analytics_custom_dimensions_create(
            website_id="abc-123",
            name="Campaign Source",
            scope="session",
            description="UTM campaign source",
            attributes={
                "active": True,
                "case_sensitive": False,
                "extractions": [
                    {"target": "page_query_parameter", "pattern": "utm_source"}
                ]
            }
        )
        ```

        Create product dimension:
        ```python
        analytics_custom_dimensions_create(
            website_id="abc-123",
            name="Product Color",
            scope="product",
            description="Color of the product",
            attributes={
                "slot": 3
            }
        )
        ```

        Args:
            website_id: Website/App UUID
            name: Dimension name
            scope: Dimension type ("session", "event", or "product")
            attributes: Scope-specific configuration (see above)
            description: Optional description (max 300 chars)

        Returns:
            CustomDimensionItem (for session/event) or ProductCustomDimensionItem (for product)

        Raises:
            ValueError: Invalid or missing attributes for the specified scope
            RuntimeError: API request failed
        """
        try:
            client = create_piwik_client()

            match scope:
                case "session" | "event":
                    validated_attrs = StandardDimensionAttrs(**attributes)
                    extractions_dict = None
                    if validated_attrs.extractions is not None:
                        extractions_dict = [e.model_dump() for e in validated_attrs.extractions]

                    api_resp = client.analytics.create_custom_dimension(
                        website_id=website_id,
                        name=name,
                        scope=scope,
                        active=validated_attrs.active,
                        case_sensitive=validated_attrs.case_sensitive,
                        description=description,
                        slot=validated_attrs.slot,
                        extractions=extractions_dict,
                    )
                    return CustomDimensionItem(**api_resp.model_dump())

                case "product":
                    validated_attrs = ProductDimensionAttrs(**attributes)
                    api_resp = client.analytics.create_product_custom_dimension(
                        website_id=website_id,
                        name=name,
                        slot=validated_attrs.slot,
                        description=description,
                    )
                    return ProductCustomDimensionItem(**api_resp.model_dump())
                case _:
                    raise ValueError(f"Invalid scope: {scope}. Must be 'session', 'event', or 'product'")

        except Exception as e:
            raise RuntimeError(f"Unexpected error creating custom dimension: {type(e).__name__}: {str(e)}")

    @mcp.tool(annotations={"title": "Piwik PRO: List Custom Dimensions", "readOnlyHint": True})
    def analytics_custom_dimensions_list(
        website_id: str,
        scope: Optional[Literal["session", "event", "product"]] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Union[CustomDimensionsList, ProductCustomDimensionsList, UnifiedCustomDimensionsList]:
        """
        List custom dimensions, optionally filtered by scope.

        Args:
            website_id: Website/App UUID
            scope: Optional scope filter:
                   - "session": Returns only session-scoped dimensions
                   - "event": Returns only event-scoped dimensions
                   - "product": Returns only product dimensions
                   - None (default): Returns both standard and product dimensions separately
            limit: Maximum number of rows to return (default: 10, min: 1, max: 100000)
                   Note: Only applies to standard dimensions (session/event). Product dimensions
                   are not paginated by the API.
            offset: Number of rows to skip (default: 0, min: 0)
                   Note: Only applies to standard dimensions (session/event).

        Returns:
            - If scope is "session" or "event": CustomDimensionsList (filtered by scope)
            - If scope is "product": ProductCustomDimensionsList
            - If scope is None: UnifiedCustomDimensionsList with both standard and product dimensions

        Raises:
            RuntimeError: If API request fails
        """
        try:
            client = create_piwik_client()

            if scope in ("session", "event"):
                # Fetch standard dimensions and filter by scope
                standard_resp = client.analytics.list_custom_dimensions(
                    website_id=website_id,
                    limit=limit,
                    offset=offset,
                )
                # Filter by scope
                filtered_data = [d for d in standard_resp.data if d.attributes.scope == scope]
                return CustomDimensionsList(
                    data=filtered_data,
                    meta={"total": len(filtered_data)} if standard_resp.meta else None,
                )

            elif scope == "product":
                # Fetch product dimensions
                product_resp = client.analytics.list_product_custom_dimensions(website_id=website_id)
                return ProductCustomDimensionsList(**product_resp.model_dump())

            elif scope is None:
                # Fetch both standard and product dimensions
                standard_resp = client.analytics.list_custom_dimensions(
                    website_id=website_id,
                    limit=limit,
                    offset=offset,
                )
                product_resp = client.analytics.list_product_custom_dimensions(website_id=website_id)

                return UnifiedCustomDimensionsList(
                    standard=CustomDimensionsList(**standard_resp.model_dump()),
                    product=ProductCustomDimensionsList(**product_resp.model_dump()),
                )

            else:
                raise ValueError(f"Invalid scope: {scope}. Must be 'session', 'event', 'product', or None")

        except ValueError:
            raise
        except PiwikProAPIError as api_err:
            error_msg = f"Failed to list custom dimensions (HTTP {api_err.status_code}): {api_err.message}"
            raise RuntimeError(error_msg)
        except Exception as e:
            raise RuntimeError(f"Unexpected error listing custom dimensions: {type(e).__name__}: {str(e)}")

    @mcp.tool(annotations={"title": "Piwik PRO: Get Custom Dimension", "readOnlyHint": True})
    def analytics_custom_dimensions_get(
        dimension_id: str,
        website_id: str,
        scope: Literal["session", "event", "product"],
    ) -> Union[CustomDimensionItem, ProductCustomDimensionItem]:
        """
        Get a specific custom dimension by ID.

        Note: The scope parameter is required to determine which API to query.
        If you don't know the scope, use analytics_custom_dimensions_list() first
        to find the dimension and its scope.

        Args:
            dimension_id: Custom Dimension UUID
            website_id: Website/App UUID
            scope: Dimension scope (required for API routing):
                   - "session" or "event": Query standard custom dimensions API
                   - "product": Query product custom dimensions API

        Returns:
            CustomDimensionItem (for session/event) or ProductCustomDimensionItem (for product)

        Raises:
            RuntimeError: If dimension not found or API request fails
        """
        try:
            client = create_piwik_client()

            if scope in ("session", "event"):
                api_resp = client.analytics.get_custom_dimension(
                    dimension_id=dimension_id,
                    website_id=website_id,
                )
                return CustomDimensionItem(**api_resp.model_dump())

            elif scope == "product":
                api_resp = client.analytics.get_product_custom_dimension(
                    dimension_id=dimension_id,
                    website_id=website_id,
                )
                return ProductCustomDimensionItem(**api_resp.model_dump())

            else:
                raise ValueError(f"Invalid scope: {scope}. Must be 'session', 'event', or 'product'")

        except PiwikProAPIError as api_err:
            error_msg = f"Failed to get custom dimension (HTTP {api_err.status_code}): {api_err.message}"
            raise RuntimeError(error_msg)
        except Exception as e:
            raise RuntimeError(f"Unexpected error getting custom dimension: {type(e).__name__}: {str(e)}")

    @mcp.tool(annotations={"title": "Piwik PRO: Update Custom Dimension"})
    def analytics_custom_dimensions_update(
        dimension_id: str,
        website_id: str,
        name: str,
        scope: Literal["session", "event", "product"],
        attributes: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
    ) -> Union[CustomDimensionItem, ProductCustomDimensionItem]:
        """
        Update an existing custom dimension with scope-specific configuration.

        ═══════════════════════════════════════════════════════════════
        COMMON PARAMETERS (all dimension types)
        ═══════════════════════════════════════════════════════════════

        • dimension_id (str): Dimension UUID
        • website_id (str): Website/App UUID
        • name (str): Updated dimension name
        • scope (str): Dimension type (needed for API routing, cannot be changed)
        • description (str, optional): Updated description (max 300 chars)

        ═══════════════════════════════════════════════════════════════
        SCOPE-SPECIFIC ATTRIBUTES
        ═══════════════════════════════════════════════════════════════

        ┌─────────────────────────────────────────────────────────────┐
        │ For scope="session" or scope="event"                        │
        │ (Standard custom dimensions)                                │
        └─────────────────────────────────────────────────────────────┘

        Required attributes:
          • active (bool)
              Whether dimension is active

          • case_sensitive (bool)
              Whether dimension values are case-sensitive

        Optional attributes:
          • extractions (list of objects)
              Updated value extraction rules

        NOTE: slot is readonly and CANNOT be updated for standard dimensions

        Example attributes:
        ```json
        {
          "active": false,
          "case_sensitive": true,
          "extractions": []
        }
        ```

        ┌─────────────────────────────────────────────────────────────┐
        │ For scope="product"                                         │
        │ (Product custom dimensions)                                 │
        └─────────────────────────────────────────────────────────────┘

        ⚠️  Product dimensions do NOT support attribute updates.

        The slot number CANNOT be changed after creation.

        The 'attributes' parameter is not required. Omit it entirely.

        ═══════════════════════════════════════════════════════════════
        EXAMPLES
        ═══════════════════════════════════════════════════════════════

        Update session dimension (deactivate):
        ```python
        analytics_custom_dimensions_update(
            dimension_id="dim-123",
            website_id="abc-123",
            name="Campaign Source",
            scope="session",
            attributes={
                "active": False,
                "case_sensitive": False
            }
        )
        ```

        Update product dimension (name and description only):
        ```python
        analytics_custom_dimensions_update(
            dimension_id="dim-456",
            website_id="abc-123",
            name="Updated Product Color",
            scope="product",
            description="Updated color attribute for products"
            # attributes parameter omitted - not needed for product dimensions
        )
        ```

        Args:
            dimension_id: Dimension UUID
            website_id: Website/App UUID
            name: Updated name
            scope: Dimension type (for API routing, cannot be changed)
            attributes: Scope-specific configuration (see above)
            description: Updated description

        Returns:
            CustomDimensionItem (for session/event) or ProductCustomDimensionItem (for product)

        Raises:
            ValueError: Invalid or missing attributes for the specified scope
            RuntimeError: API request failed
        """
        try:
            client = create_piwik_client()

            match scope:
                case "session" | "event":
                    validated_attrs = StandardDimensionUpdateAttrs(**attributes)

                    # Convert validated extractions to dict format
                    extractions_dict = None
                    if validated_attrs.extractions is not None:
                        extractions_dict = [e.model_dump() for e in validated_attrs.extractions]

                    # Call API with validated attributes
                    api_resp = client.analytics.update_custom_dimension(
                        dimension_id=dimension_id,
                        website_id=website_id,
                        name=name,
                        active=validated_attrs.active,
                        case_sensitive=validated_attrs.case_sensitive,
                        description=description,
                        extractions=extractions_dict,
                    )
                    return CustomDimensionItem(**api_resp.model_dump())
                case "product":
                    validated_attrs = ProductDimensionUpdateAttrs(**attributes)
                    api_resp = client.analytics.update_product_custom_dimension(
                        dimension_id=dimension_id,
                        website_id=website_id,
                        name=name,
                        description=description,
                    )
                    return ProductCustomDimensionItem(**api_resp.model_dump())
                case _:
                    raise ValueError(f"Invalid scope: {scope}. Must be 'session', 'event', or 'product'")

        except PiwikProAPIError as api_err:
            error_msg = f"Failed to update custom dimension (HTTP {api_err.status_code}): {api_err.message}"
            raise RuntimeError(error_msg)
        except Exception as e:
            raise RuntimeError(f"Unexpected error updating custom dimension: {type(e).__name__}: {str(e)}")

    @mcp.tool(annotations={"title": "Piwik PRO: Get Custom Dimension Slots", "readOnlyHint": True})
    def analytics_custom_dimensions_get_slots(
        website_id: str,
    ) -> CustomDimensionSlotsInfo:
        """
        Get slot availability statistics for all dimension types.

        This endpoint provides information about how many dimension slots are available,
        used, and remaining for each scope (session, event, and product).

        Args:
            website_id: Website/App UUID

        Returns:
            Slot statistics for all dimension scopes with the following info for each:
            - available: Total number of slots available
            - used: Number of slots currently in use
            - left: Number of slots remaining

        Raises:
            RuntimeError: If API request fails
        """
        try:
            client = create_piwik_client()
            api_resp = client.analytics.get_custom_dimension_slots(website_id=website_id)
            return CustomDimensionSlotsInfo(**api_resp.model_dump())
        except PiwikProAPIError as api_err:
            error_msg = f"Failed to get custom dimension slots (HTTP {api_err.status_code}): {api_err.message}"
            raise RuntimeError(error_msg)
        except Exception as e:
            raise RuntimeError(f"Unexpected error getting custom dimension slots: {type(e).__name__}: {str(e)}")
