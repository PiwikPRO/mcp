"""
Pydantic models for Analytics API responses (Annotations, Goals, and Custom Dimensions).
"""

import re
from enum import StrEnum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, RootModel, model_validator

from ..common import Meta


class AnnotationAuthor(BaseModel):
    """Annotation author info (present for user annotations)."""

    email: str = Field(..., description="Email address of the author")


class UserAnnotationAttributes(BaseModel):
    """Attributes for a user annotation (JSON:API)."""

    date: str = Field(..., description="Annotation date (YYYY-MM-DD)")
    content: str = Field(..., description="Annotation content")
    visibility: Optional[str] = Field(None, description='"private" or "public"')
    website_id: Optional[str] = Field(None, description="App UUID associated with the annotation")
    author: Optional[AnnotationAuthor] = Field(None, description="Author info")
    is_author: Optional[bool] = Field(None, description="Whether current user is the author")


class SystemAnnotationAttributes(BaseModel):
    """Attributes for a system annotation (JSON:API)."""

    date: str = Field(..., description="Annotation date (YYYY-MM-DD)")
    content: str = Field(..., description="Annotation content")


class UserAnnotationResource(BaseModel):
    """User annotation resource."""

    id: str = Field(..., description="Annotation UUID")
    type: Literal["UserAnnotation"]
    attributes: UserAnnotationAttributes


class SystemAnnotationResource(BaseModel):
    """System annotation resource."""

    id: str = Field(..., description="Annotation UUID")
    type: Literal["SystemAnnotation"]
    attributes: SystemAnnotationAttributes


class UserAnnotationSingleResponse(BaseModel):
    """
    Response model for single annotation (user or system).
    """

    data: UserAnnotationResource = Field(..., description="User annotation resource")


class SystemAnnotationListResponse(BaseModel):
    """
    Response model for system annotations list endpoints.
    """

    data: List[SystemAnnotationResource] = Field(..., description="List of system annotation resources")
    meta: Meta = Field(..., description="Pagination metadata with total count")


class UserAnnotationListResponse(BaseModel):
    """
    Response model for user annotations list endpoints.
    """

    data: List[UserAnnotationResource] = Field(..., description="List of user annotation resources")
    meta: Meta = Field(..., description="Pagination metadata with total count")


class GoalAttributes(BaseModel):
    """Attributes for a Goal (JSON:API)."""

    website_id: str = Field(..., description="Website/App UUID")
    name: str = Field(..., description="Name of the goal")
    description: Optional[str] = Field(None, description="Description of the goal (max 1024 chars)")
    trigger: Literal[
        "url",
        "title",
        "event_name",
        "event_category",
        "event_action",
        "file",
        "external_website",
        "manually",
    ] = Field(..., description="Trigger type for the goal")
    pattern_type: Optional[Literal["contains", "exact", "regex"]] = Field(
        None,
        description='Condition operator for pattern matching. Required for all triggers except "manually".',
    )
    pattern: Optional[str] = Field(
        None,
        description='Condition value to match against. Required for all triggers except "manually".',
    )
    allow_multiple: Optional[bool] = Field(
        None,
        description="Whether the goal can be converted more than once per visit",
    )
    case_sensitive: Optional[bool] = Field(
        None,
        description="Whether pattern matching is case sensitive",
    )
    revenue: str = Field(..., description='Goal revenue value as string in monetary format (e.g., "10.22" or "0")')


class GoalResource(BaseModel):
    """Goal resource."""

    id: str = Field(..., description="Goal UUID")
    type: Literal["Goal"]
    attributes: GoalAttributes


class GoalSingleResponse(BaseModel):
    """Response model for single goal."""

    data: GoalResource = Field(..., description="Goal resource")


class GoalListResponse(BaseModel):
    """Response model for goals list endpoints."""

    data: List[GoalResource] = Field(..., description="List of goal resources")
    meta: Meta = Field(..., description="Pagination metadata with total count")


class FilterCondition(BaseModel):
    operator: str
    value: str | int | float | bool | None = None


class StringFilterCondition(FilterCondition):
    operator: Literal[
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
    ] = Field(description="For 'matches' and 'not_matches' use re2 syntax")
    value: str | None = None


class NumericFilterCondition(FilterCondition):
    operator: Literal["eq", "neq", "gt", "gte", "lt", "lte"]
    value: int | float | None = None


class BooleanFilterCondition(FilterCondition):
    operator: Literal["eq", "neq"]
    value: bool | None = None


class EnumFilterCondition(FilterCondition):
    operator: Literal["eq", "neq", "empty", "not_empty"]
    value: str | None = None


class ColumnFilter(BaseModel):
    """Filter on a specific column."""

    column_id: str
    condition: StringFilterCondition | NumericFilterCondition | BooleanFilterCondition | EnumFilterCondition


class FilterGroup(BaseModel):
    """Group of filters with logical operator."""

    operator: Literal["and", "or"]
    conditions: list["ColumnFilter | FilterGroup"]


class RelativeDate(StrEnum):
    TODAY = "today"
    YESTERDAY = "yesterday"
    LAST_WEEK = "last_week"
    LAST_MONTH = "last_month"
    LAST_YEAR = "last_year"


# Column metadata - shared structure between dimensions and metrics
class ColumnMeta(BaseModel):
    """Metadata describing a column (dimension or metric)."""

    column_name: str
    column_type: str  # str, int, float, bool, hex, array, etc.
    column_category: list[str] = Field(default_factory=list)
    column_unit: str | None = None  # days, seconds, pixels, url, percentage, etc.
    is_internal: bool | None = None
    is_visible: bool | None = None
    scope: str | None = None  # "session" or "event"
    is_nullable: bool | None = None
    is_negative_metric: bool | None = None
    is_rtr_compatible: bool | None = None
    is_google_search: bool | None = None
    is_google_ads: bool | None = None
    # For metrics only
    # should be list[ColumnDefinition] but it doesn't work properly
    source_metrics: list[dict] = Field(default_factory=list)
    description: str | None = None
    show_total_percentage: bool | None = None


class ColumnDefinition(BaseModel):
    """A dimension or metric column definition."""

    column_id: str
    requires_events: bool
    column_meta: ColumnMeta
    # For calculated metrics only
    calculated_metric_id: str | None = None
    # For custom channel groupings only
    custom_channel_grouping_id: str | None = None


class TransformationInfo(BaseModel):
    """Information about an available transformation."""

    transformation_id: str
    result_type: str


class TransformationDVGInfo(TransformationInfo):
    dimension_value_grouping_id: str = Field(..., description="Only for dimension value groupings")
    dimension_value_grouping_name: str = Field(..., description="Only for dimension value groupings")


class AvailableTransformations(BaseModel):
    """Available transformations for a dimension."""

    dimension_to_metric: list[TransformationInfo] = Field(default_factory=list)
    dimension_to_dimension: list[TransformationInfo | TransformationDVGInfo] = Field(default_factory=list)


class DimensionColumnDefinition(ColumnDefinition):
    """A dimension column definition."""

    enum_values: Dict[str, Any] | None = None
    available_transformations: AvailableTransformations | None = None


class MetricColumnInput(BaseModel):
    column_id: str = Field(..., description="Metric ID")
    transformation_id: Literal["unique_count", "min", "max", "average", "median", "sum"] | None = None
    goal_id: int | None = Field(None, description="Optional goal ID")
    calculated_metric_id: str | None = Field(None, description="Only for calculated metrics")
    event_type: int | None = Field(None, description="Only for metrics with scope 'product'")


class DimensionColumnInput(BaseModel):
    column_id: str = Field(..., description="Dimension ID")
    transformation_id: (
        Literal[
            "to_date",
            "to_start_of_hour",
            "to_start_of_week",
            "to_start_of_month",
            "to_start_of_quarter",
            "to_start_of_year",
            "to_hour_of_day",
            "to_day_of_week",
            "to_month_number",
            "to_start_of_minute",
            "to_start_of_five_minutes",
            "to_start_of_ten_minutes",
            "lower",
            "to_path",
            "to_domain",
            "strip_qs",
            "group_dimension_values",
            "dimension_value_grouping",
        ]
        | None
    ) = None
    custom_channel_grouping_id: str | None = Field(None, description="Only for custom channel groupings")
    dimension_value_grouping_id: str | None = Field(None, description="Only for dimension value groupings")


class QueryRequest(BaseModel):
    """Request model for analytics query."""

    website_id: str = Field(description="Website/app UUID")
    columns: list[MetricColumnInput | DimensionColumnInput] = Field(description="Columns to retrieve")
    date_from: str | None = Field(
        None,
        description=(
            "Start date in YYYY-MM-DD format. "
            "Cannot be used with relative_date field at the same time. "
            "Mandatory if relative_date is not used."
        ),
    )
    date_to: str | None = Field(
        None,
        description=(
            "End date in YYYY-MM-DD format. "
            "Cannot be used with relative_date field at the same time. "
            "Mandatory if relative_date is not used."
        ),
    )
    relative_date: RelativeDate | str | None = Field(
        None,
        description=(
            "Relative date (today, yesterday, last_week, last_month, last_year, last_X_days). "
            "Cannot be used with absolute date fields (date_from, date_to) at the same time. "
            "last_X_days must be in range 1 <= X <= 365"
        ),
    )
    filters: FilterGroup | None = Field(None, description="Dimension filtering conditions")
    metric_filters: FilterGroup | None = Field(None, description="Metric filtering conditions")
    offset: int | None = Field(0, ge=0, description="Number of rows to skip")
    limit: int | None = Field(100, ge=1, le=100000, description="Maximum rows to return")
    order_by: list[list[Any]] | None = Field(None, description="Order by column index and direction")

    @model_validator(mode="after")
    def validate_date_fields(self):
        has_absolute = self.date_from is not None or self.date_to is not None
        has_relative = self.relative_date is not None

        if has_absolute and has_relative:
            raise ValueError("Cannot use relative_date with date_from/date_to")

        if not has_absolute and not has_relative:
            raise ValueError("Must provide either relative_date or both date_from and date_to")

        if has_absolute and (self.date_from is None or self.date_to is None):
            raise ValueError("Both date_from and date_to are required when using absolute dates")

        if has_relative and isinstance(self.relative_date, str) and self.relative_date not in RelativeDate:
            match = re.fullmatch(r"last_(\d+)_days", self.relative_date)
            if not match:
                raise ValueError(f"Invalid relative_date: {self.relative_date}")
            days = int(match.group(1))
            if not 1 <= days <= 365:
                raise ValueError(f"last_X_days requires X in range 1-365, got {days}")

        return self


class QueryResponseMeta(BaseModel):
    """Metadata for query response."""

    columns: list[str]
    count: int


class QueryResponse(BaseModel):
    """Response model for analytics query."""

    data: list[list[Any]]
    meta: QueryResponseMeta


class DimensionsListResponse(RootModel[list[ColumnDefinition]]):
    """Response from dimensions list endpoint."""

    pass


class MetricsListResponse(RootModel[list[ColumnDefinition]]):
    """Response from metrics list endpoint."""

    pass


# Custom Dimensions Models


class ExtractionConfig(BaseModel):
    """Extraction configuration for custom dimensions."""

    target: Literal["page_title_regex", "page_url_regex", "page_query_parameter"] = Field(
        ...,
        description="What value should be extracted",
    )
    pattern: str = Field(
        ...,
        description="Pattern for regexes or exact match on query param",
    )


class CustomDimensionAttributes(BaseModel):
    """Attributes for a standard Custom Dimension."""

    website_id: str = Field(..., description="Website/App UUID")
    name: str = Field(..., description="Name of the custom dimension")
    description: Optional[str] = Field(None, max_length=300, description="Description (max 300 chars)")
    active: bool = Field(..., description="Whether dimension is active")
    case_sensitive: bool = Field(..., description="Whether dimension is case sensitive")
    scope: Literal["session", "event"] = Field(..., description="Dimension scope (session or event level)")
    tracking_id: Optional[int] = Field(None, ge=1, description="Tracking ID (readonly)")
    slot: Optional[int] = Field(None, ge=1, description="Slot number (readonly after creation)")
    extractions: Optional[List[ExtractionConfig]] = Field(
        None,
        description="Value extraction configurations",
    )


class CustomDimensionResource(BaseModel):
    """Standard Custom Dimension resource."""

    id: str = Field(..., description="Custom Dimension UUID")
    type: Literal["CustomDimension"]
    attributes: CustomDimensionAttributes


class CustomDimensionSingleResponse(BaseModel):
    """Response for single custom dimension operations."""

    data: CustomDimensionResource


class CustomDimensionListResponse(BaseModel):
    """Response for list custom dimensions."""

    data: List[CustomDimensionResource]
    meta: Optional[Meta] = None


class ProductCustomDimensionAttributes(BaseModel):
    """Attributes for a Product Custom Dimension."""

    website_id: str = Field(..., description="Website/App UUID")
    name: str = Field(..., description="Name of the product custom dimension")
    description: Optional[str] = Field(None, max_length=300, description="Description (max 300 chars)")
    slot: int = Field(..., ge=1, description="Slot number")
    created_at: Optional[str] = Field(None, description="Creation datetime (readonly)")
    updated_at: Optional[str] = Field(None, description="Last update datetime (readonly)")


class ProductCustomDimensionResource(BaseModel):
    """Product Custom Dimension resource."""

    id: str = Field(..., description="Product Custom Dimension UUID")
    type: Literal["ProductCustomDimension"]
    attributes: ProductCustomDimensionAttributes


class ProductCustomDimensionSingleResponse(BaseModel):
    """Response for single product custom dimension operations."""

    data: ProductCustomDimensionResource


class ProductCustomDimensionListResponse(BaseModel):
    """Response for list product custom dimensions."""

    data: List[ProductCustomDimensionResource]
    meta: Optional[Meta] = None


class CustomDimensionSlotInfo(BaseModel):
    """Slot availability information for a specific scope."""

    available: int = Field(..., description="Total available slots")
    used: int = Field(..., description="Number of slots currently used")
    left: int = Field(..., description="Number of slots remaining")


class CustomDimensionSlotsAttributes(BaseModel):
    """Slot statistics by scope."""

    event: Optional[CustomDimensionSlotInfo] = Field(None, description="Event-scoped dimension slots")
    session: Optional[CustomDimensionSlotInfo] = Field(None, description="Session-scoped dimension slots")
    product: Optional[CustomDimensionSlotInfo] = Field(None, description="Product dimension slots")


class CustomDimensionSlotsResource(BaseModel):
    """Slots statistics resource."""

    type: Literal["CustomDimensionStatistics"]
    id: str = Field(..., description="Website UUID")
    attributes: CustomDimensionSlotsAttributes


class CustomDimensionSlotsResponse(BaseModel):
    """Response for slots endpoint."""

    data: CustomDimensionSlotsResource


class DimensionValueGroupingItem(BaseModel):
    """Single dimension value grouping item."""

    id: str
    website_id: str | None
    name: str
    author: dict[Literal["email"], str]
    is_author: bool
    column_id: str
    column_meta: ColumnMeta
    visibility: str
    is_global: bool
    created_at: str
    updated_at: str


class DimensionValueGroupingListResponse(BaseModel):
    """Response for listing dimension value groupings."""

    count: int
    results: list[DimensionValueGroupingItem]
