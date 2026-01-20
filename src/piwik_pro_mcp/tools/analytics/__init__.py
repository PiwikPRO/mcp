"""
Analytics tools for Piwik PRO MCP server.

This module provides MCP tools for managing Analytics user annotations, goals, and custom dimensions.
"""

from mcp.server.fastmcp import FastMCP

from .annotations import register_annotations_tools
from .custom_dimensions import register_custom_dimensions_tools
from .goals import register_goals_tools
from .models import (
    AnnotationItem,
    AnnotationResource,
    AnnotationsList,
    CustomDimensionItem,
    CustomDimensionsList,
    CustomDimensionSlotsInfo,
    GoalItem,
    GoalsList,
    ProductCustomDimensionItem,
    ProductCustomDimensionsList,
    QueryExecuteResponse,
    UnifiedCustomDimensionsList,
)
from .query import register_query_tools
from .validators import (
    ExtractionConfigDict,
    ProductDimensionAttrs,
    StandardDimensionAttrs,
    StandardDimensionUpdateAttrs,
)


def register_analytics_tools(mcp: FastMCP) -> None:
    """
    Register all Analytics tools with the MCP server.

    This includes:
    - User annotations tools
    - Goals tools
    - Query tools
    - Custom dimensions tools (unified standard and product dimensions)

    Args:
        mcp: FastMCP server instance
    """
    register_annotations_tools(mcp)
    register_goals_tools(mcp)
    register_query_tools(mcp)
    register_custom_dimensions_tools(mcp)


__all__ = [
    # Registration
    "register_analytics_tools",
    # Models
    "AnnotationsList",
    "AnnotationItem",
    "AnnotationResource",
    "GoalsList",
    "GoalItem",
    "QueryExecuteResponse",
    "CustomDimensionsList",
    "CustomDimensionItem",
    "ProductCustomDimensionsList",
    "ProductCustomDimensionItem",
    "UnifiedCustomDimensionsList",
    "CustomDimensionSlotsInfo",
    "ExtractionConfig",
    # Validators
    "ExtractionConfigDict",
    "StandardDimensionAttrs",
    "StandardDimensionUpdateAttrs",
    "ProductDimensionAttrs",
]
