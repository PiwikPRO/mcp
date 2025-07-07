"""
Parameter discovery system for MCP tools.

This module provides the parameter discovery functionality that allows tools
to expose their JSON schemas for dynamic parameter exploration.
"""

from mcp.server.fastmcp import FastMCP

from ..common.tool_schemas import get_tool_schema


def register_parameter_discovery_tool(mcp: FastMCP) -> None:
    """Register the parameter discovery tool with the MCP server."""

    @mcp.tool(annotations={"title": "Piwik PRO: Get Tool Parameters Schema", "readOnlyHint": True})
    def tools_parameters_get(tool_name: str) -> dict:
        """Get JSON schema for tool parameters.

        This tool provides parameter discovery for MCP tools that use JSON attributes.
        It returns the complete JSON schema including field types, descriptions,
        validation rules, and examples for tools that have been refactored to use
        the simplified JSON attributes interface.

        Args:
            tool_name: Name of the MCP tool to get parameters for (e.g., "apps_update")

        Returns:
            Dictionary containing JSON schema for the tool's parameters including:
            - type: Object type definition
            - properties: Field definitions with types and descriptions
            - required: List of required fields (usually empty for update tools)
            - definitions: Enum and complex type definitions

        Example Usage:
            schema = tools_parameters_get("apps_update")
            # Returns complete JSON schema with all 19 available fields

        Raises:
            ValueError: If tool_name is not recognized
        """
        return get_tool_schema(tool_name)
