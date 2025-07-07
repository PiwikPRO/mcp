"""
CDP attribute management functions.

This module provides functionality for listing and processing CDP attributes,
including operator validation and value format handling.
"""

from typing import Any, Dict, List

from piwik_pro_mcp.api.exceptions import BadRequestError, NotFoundError

from ...common.utils import create_piwik_client
from .models import AttributeListMCPResponse, AttributeSummary

# Operator mappings based on Piwik PRO CDP API documentation
OPERATOR_MAPPINGS: Dict[str, List[str]] = {
    "number": ["eq", "neq", "gt", "gte", "lt", "lte"],
    "string": [
        "eq",
        "neq",
        "contains",
        "not_contains",
        "icontains",
        "not_icontains",
        "starts_with",
        "ends_with",
        "matches",
        "not_matches",
    ],
    "str_nocase": [
        "eq",
        "neq",
        "contains",
        "not_contains",
        "icontains",
        "not_icontains",
        "starts_with",
        "ends_with",
        "matches",
        "not_matches",
    ],
    "ipv4": ["eq", "neq", "gt", "gte", "lt", "lte"],
    "ipv6": ["eq", "neq", "gt", "gte", "lt", "lte"],
    "bool": ["eq", "neq"],
    "int": ["eq", "neq", "gt", "gte", "lt", "lte"],
    "uuid": ["eq", "neq"],
    "hex": ["eq", "neq"],
    "datetime": ["earlier_than", "later_than", "before_last", "in_the_last", "in_the_next", "after_next"],
}

# Value format mappings for different column types
VALUE_FORMAT_MAPPINGS: Dict[str, Dict[str, Any]] = {
    "number": {
        "format": "number",
        "description": "Plain numeric value",
        "example": 500,
        "validation": "Must be a valid number (integer or float)",
    },
    "string": {
        "format": "string",
        "description": "Plain string value",
        "example": "example_value",
        "validation": "Must be a string",
    },
    "str_nocase": {
        "format": "string",
        "description": "Plain string value (case insensitive matching)",
        "example": "Example_Value",
        "validation": "Must be a string",
    },
    "ipv4": {
        "format": "string",
        "description": "IPv4 address as string",
        "example": "192.168.1.1",
        "validation": "Must be a valid IPv4 address",
    },
    "ipv6": {
        "format": "string",
        "description": "IPv6 address as string",
        "example": "2001:db8::1",
        "validation": "Must be a valid IPv6 address",
    },
    "bool": {
        "format": "boolean",
        "description": "Boolean true/false value",
        "example": True,
        "validation": "Must be true or false",
    },
    "int": {"format": "integer", "description": "Integer value", "example": 42, "validation": "Must be a whole number"},
    "uuid": {
        "format": "string",
        "description": "UUID string",
        "example": "123e4567-e89b-12d3-a456-426614174000",
        "validation": "Must be a valid UUID format",
    },
    "hex": {
        "format": "string",
        "description": "Hexadecimal string",
        "example": "1a2b3c4d",
        "validation": "Must be a valid hexadecimal string",
    },
    "datetime": {
        "format": "object",
        "description": "Object with 'value' (ISO datetime string) and 'unit' ('datetime') fields",
        "example": {"value": "2024-11-15T23:59:59Z", "unit": "datetime"},
        "validation": "Must be object with 'value' as ISO 8601 datetime string and 'unit' as 'datetime'",
        "absolute_operators": ["earlier_than", "later_than"],
        "absolute_example": {"value": "2024-11-15T23:59:59Z", "unit": "datetime"},
        "relative_operators": ["before_last", "in_the_last", "in_the_next", "after_next"],
        "relative_example": {"value": 30, "unit": "days"},
    },
}

# Default value format for unknown types
DEFAULT_VALUE_FORMAT: Dict[str, Any] = {
    "format": "unknown",
    "description": "Unknown format - check API documentation",
    "example": None,
    "validation": "Format not defined for this column type",
}


def get_supported_operators_for_column_type(column_type: str) -> List[str]:
    """
    Get supported operators for a specific column type.

    Args:
        column_type: The column type (number, string, datetime, etc.)

    Returns:
        List of supported operators for this column type
    """
    return OPERATOR_MAPPINGS.get(column_type, [])


def get_value_format_for_column_type(column_type: str) -> Dict[str, Any]:
    """
    Get value format specification for a specific column type.

    Args:
        column_type: The column type (number, string, datetime, etc.)

    Returns:
        Dictionary containing format specification with description, example, and validation rules
    """
    return VALUE_FORMAT_MAPPINGS.get(column_type, DEFAULT_VALUE_FORMAT)


def list_cdp_attributes(app_id: str) -> AttributeListMCPResponse:
    """
    List all CDP attributes available for audience creation.

    Returns the raw API response containing attribute metadata including:
    - column_id: Unique identifier for the attribute
    - column_meta: Metadata with column_name, column_type, value_selectors, etc.
    - immutable: Whether the attribute is read-only
    - event_data_key: Key for imported data

    Args:
        app_id: UUID of the app to list attributes for

    Returns:
        AttributeListMCPResponse containing the raw API response with attribute list

    Raises:
        RuntimeError: If authentication fails or API request fails
    """
    try:
        client = create_piwik_client()
        response = client.cdp.list_attributes(app_id=app_id)

        if not response:
            return AttributeListMCPResponse(attributes=[], total=0)

        # Transform response into structured AttributeSummary objects
        attributes_data = []
        for attr in response:
            column_meta = attr.get("column_meta", {})
            column_type = column_meta.get("column_type", "unknown")
            attributes_data.append(
                AttributeSummary(
                    column_id=attr.get("column_id", ""),
                    event_data_key=attr.get("event_data_key", ""),
                    immutable=attr.get("immutable", False),
                    column_name=column_meta.get("column_name", ""),
                    column_type=column_type,
                    column_category=column_meta.get("column_category", []),
                    value_selectors=column_meta.get("value_selectors", ["none"]),
                    scope=column_meta.get("scope", "unknown"),
                    column_unit=column_meta.get("column_unit"),
                    supported_operators=get_supported_operators_for_column_type(column_type),
                    value_format=get_value_format_for_column_type(column_type),
                )
            )

        return AttributeListMCPResponse(attributes=attributes_data, total=len(attributes_data))

    except (BadRequestError, NotFoundError) as e:
        raise RuntimeError(f"Failed to list CDP attributes: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error listing CDP attributes: {e}")
