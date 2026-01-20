"""
Pydantic models for MCP Analytics tool responses (Annotations, Goals, and Custom Dimensions).
"""

from typing import Any, Dict, List, Union

from pydantic import BaseModel, Field

from piwik_pro_mcp.api.methods.analytics.models import (
    ColumnDefinition,
    CustomDimensionResource,
    CustomDimensionSlotsResource,
    DimensionColumnDefinition,
    GoalResource,
    ProductCustomDimensionResource,
    QueryResponse,
    SystemAnnotationResource,
    UserAnnotationResource,
)

AnnotationResource = Union[UserAnnotationResource, SystemAnnotationResource]


class AnnotationsList(BaseModel):
    """Combined list output for annotations_list tool."""

    data: List[AnnotationResource] = Field(..., description="List of annotations")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Metadata such as total count")


class AnnotationItem(BaseModel):
    """Single annotation output for create/get/update tools."""

    data: AnnotationResource


class GoalsList(BaseModel):
    """List output for goals_list tool."""

    data: List[GoalResource] = Field(..., description="List of goals")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Metadata such as total count")


class GoalItem(BaseModel):
    """Single goal output for create/get/update tools."""

    data: GoalResource


class QueryExecuteResponse(BaseModel):
    """Response from query execution."""

    status: str = Field(description="Execution status")
    result: QueryResponse = Field(description="Query results")
    message: str = Field(description="Status message")


class DimensionsList(BaseModel):
    """Response for analytics_list_dimensions tool."""

    dimensions: dict[str, str]
    custom_channel_groupings: dict[str, str]


class MetricsList(BaseModel):
    """Response for analytics_list_metrics tool."""

    metrics: dict[str, str]
    calculated_metrics: dict[str, str]


class DimensionsDetailsList(BaseModel):
    """Response for analytics_list_details_dimensions tool."""

    dimensions: list[DimensionColumnDefinition]
    custom_channel_groupings: list[ColumnDefinition]


class MetricsDetailsList(BaseModel):
    """Response for analytics_list_details_metrics tool."""

    metrics: list[ColumnDefinition]
    calculated_metrics: list[ColumnDefinition]


# Custom Dimensions Tool Response Models


class CustomDimensionsList(BaseModel):
    """List output for custom_dimensions_list tool (standard dimensions)."""

    data: List[CustomDimensionResource] = Field(..., description="List of custom dimensions")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Metadata such as total count")


class CustomDimensionItem(BaseModel):
    """Single custom dimension output for create/get/update tools (standard dimensions)."""

    data: CustomDimensionResource


class ProductCustomDimensionsList(BaseModel):
    """List output for custom_dimensions_list tool (product dimensions)."""

    data: List[ProductCustomDimensionResource] = Field(..., description="List of product custom dimensions")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Metadata such as total count")


class ProductCustomDimensionItem(BaseModel):
    """Single product custom dimension output for create/get/update tools."""

    data: ProductCustomDimensionResource


class UnifiedCustomDimensionsList(BaseModel):
    """Unified list output when scope=None (returns both standard and product dimensions)."""

    standard: CustomDimensionsList = Field(..., description="Standard custom dimensions (session/event)")
    product: ProductCustomDimensionsList = Field(..., description="Product custom dimensions")


class CustomDimensionSlotsInfo(BaseModel):
    """Slots availability information for all dimension types."""

    data: CustomDimensionSlotsResource
