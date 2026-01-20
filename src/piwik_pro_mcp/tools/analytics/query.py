from collections import defaultdict
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from piwik_pro_mcp.api.methods.analytics.models import (
    AvailableTransformations,
    ColumnDefinition,
    DimensionColumnDefinition,
    DimensionValueGroupingItem,
    TransformationDVGInfo,
    TransformationInfo,
)
from piwik_pro_mcp.common.utils import create_piwik_client, fetch_json_from_url

from .models import DimensionsDetailsList, DimensionsList, MetricsDetailsList, MetricsList, QueryExecuteResponse

DEPRECATED_METRICS = {"total_quantity", "unique_purchases"}
DEPRECATED_DIMENSIONS = {"goal_id", "location_metro_code", "item_count"}

DIMENSIONS_WITH_ENUMS = [
    "app_currency",
    "browser_language_iso639",
    "browser_name",
    "consent_action",
    "consent_form_button",
    "consent_scope",
    "consent_source",
    "device_brand",
    "device_type",
    "event_type",
    "google_ads_ad_network_type",
    "google_ads_currency",
    "google_ads_keyword_match_type",
    "location_continent_iso_code",
    "location_metro_code",
    "operating_system",
    "referrer_type",
    "session_ecommerce_status",
    "sharepoint_action",
    "sharepoint_object_type",
    "tracked_currency",
    "visitor_returning",
]

DIMENSIONS_URL_PREFIX = "https://ppdevelopersportal.z1.web.core.windows.net/assets/enums/"

# Dimension to Metric transformations (aggregations)
METRIC_TRANSFORMATIONS = {
    "unique_count": {"source_types": {"int", "str"}, "result_type": "int"},
    "min": {"source_types": {"float", "int"}, "result_type": None},
    "max": {"source_types": {"float", "int"}, "result_type": None},
    "average": {"source_types": {"float", "int"}, "result_type": "float"},
    "median": {"source_types": {"float", "int"}, "result_type": None},
    "sum": {"source_types": {"float", "int"}, "result_type": None},
}

# Dimension to Dimension transformations
DIMENSION_TRANSFORMATIONS = {
    "to_date": {"source_types": {"date", "datetime"}, "result_type": "date"},
    "to_start_of_hour": {"source_types": {"datetime"}, "result_type": "datetime"},
    "to_start_of_week": {"source_types": {"date", "datetime"}, "result_type": "date"},
    "to_start_of_month": {"source_types": {"date", "datetime"}, "result_type": "date"},
    "to_start_of_quarter": {"source_types": {"date", "datetime"}, "result_type": "date"},
    "to_start_of_year": {"source_types": {"date", "datetime"}, "result_type": "date"},
    "to_hour_of_day": {"source_types": {"datetime"}, "result_type": "int"},
    "to_day_of_week": {"source_types": {"date", "datetime"}, "result_type": "int"},
    "to_month_number": {"source_types": {"date", "datetime"}, "result_type": "int"},
    "to_start_of_minute": {"source_types": {"datetime"}, "result_type": "datetime"},
    "to_start_of_five_minutes": {"source_types": {"datetime"}, "result_type": "datetime"},
    "to_start_of_ten_minutes": {"source_types": {"datetime"}, "result_type": "datetime"},
    "lower": {"source_types": {"str"}, "result_type": "str"},
    "to_path": {"source_types": {"str"}, "result_type": "str"},
    "to_domain": {"source_types": {"str"}, "result_type": "str"},
    "strip_qs": {"source_types": {"str"}, "result_type": "str"},
}

# Dimensions that support group_dimension_values transformation
# These are dimensions with predefined value groupings in the API
DIMENSIONS_WITH_GROUP_VALUES = {
    "session_total_time",
    "visitor_days_since_last_session",
    "visitor_session_number",
    "session_total_page_views",
    "session_unique_page_views",
    "custom_event_value",
}

# Special dimension-specific transformations (not type-based)
DIMENSION_SPECIFIC_TRANSFORMATIONS = {
    "group_dimension_values": {
        "applicable_dimensions": DIMENSIONS_WITH_GROUP_VALUES,
        "result_type": "str",
    },
}


def get_available_transformations(
    column_id: str, column_type: str, dimension_value_groupings: list[DimensionValueGroupingItem]
) -> AvailableTransformations:
    """Return available transformations based on column type and id."""

    def build_transformations(transformations_config: dict) -> list[TransformationInfo]:
        result = []
        for trans_id, config in transformations_config.items():
            if column_type in config["source_types"]:
                # result_type None means it returns the same type as the source column
                result_type = config["result_type"] if config["result_type"] is not None else column_type
                result.append(TransformationInfo(transformation_id=trans_id, result_type=result_type))

        return result

    def build_dvg_transformations(dvgs: list[DimensionValueGroupingItem]):
        result = []
        for dvg in dvgs:
            result.append(
                TransformationDVGInfo(
                    transformation_id="dimension_value_grouping",
                    result_type=dvg.column_meta.column_type,
                    dimension_value_grouping_id=dvg.id,
                    dimension_value_grouping_name=dvg.name,
                )
            )

        return result

    def build_dimension_specific_transformations() -> list[TransformationInfo]:
        result = []
        for trans_id, config in DIMENSION_SPECIFIC_TRANSFORMATIONS.items():
            if column_id in config["applicable_dimensions"]:
                result.append(
                    TransformationInfo(
                        transformation_id=trans_id,
                        result_type=config["result_type"],
                    )
                )
        return result

    dim_to_dim = build_transformations(DIMENSION_TRANSFORMATIONS)
    dim_to_dim.extend(build_dvg_transformations(dimension_value_groupings))
    dim_to_dim.extend(build_dimension_specific_transformations())

    return AvailableTransformations(
        dimension_to_metric=build_transformations(METRIC_TRANSFORMATIONS),
        dimension_to_dimension=dim_to_dim,
    )


def register_query_tools(mcp: FastMCP) -> None:  # noqa: PLR0915
    """Register Query API tools with the MCP server."""

    @mcp.tool(annotations=ToolAnnotations(title="Piwik PRO: Execute Analytics Query", readOnlyHint=True))
    def analytics_query_execute(
        website_id: str,
        columns: list[dict[str, Any]],
        date_from: str | None = None,
        date_to: str | None = None,
        relative_date: str | None = None,
        filters: dict[str, Any] | None = None,
        metric_filters: dict[str, Any] | None = None,
        offset: int = 0,
        limit: int = 100,
        order_by: list[list[Any]] | None = None,
    ) -> QueryExecuteResponse:
        """
        Execute an analytics query against Piwik PRO.

        REQUIRED WORKFLOW - You must follow these steps in order:

        1. Call `analytics_dimensions_list` to get available dimension IDs
        2. Call `analytics_metrics_list` to get available metric IDs
        3. Call `analytics_dimensions_details_list` for details on dimensions you plan to use
        4. Call `analytics_metrics_details_list` for details on metrics you plan to use
        5. Call this tool with validated column_ids and transformation_ids

        Column IDs and transformation IDs must exactly match values returned by the list and
        details endpoints. Guessing or inventing IDs will cause query failures.

        DO NOT RUN THIS TOOL BEFORE CHECKING DIMENSIONS AND METRICS DETAILS!
        Important: Metrics cannot be transformed. Only dimensions accept transformation_id.

        ---

        Args:
            website_id: UUID of the website/app to query
            columns: List of column definitions. Each column is a dict with:
                - column_id (required): Dimension or metric ID from the list endpoints
                  (in case of calculated metric use always string "calculated_metric",
                  in case of custom channel grouping use always string "custom_channel_grouping")
                - transformation_id (optional): Aggregation function from details endpoint
                  (e.g., "sum", "count", "unique_count")
                  Note: Only dimensions support transformations. Metrics cannot be transformed.
                - calculated_metric_id: only for calculated metrics
                - custom_channel_grouping_id: only for custom channel groupings
                - dimension_value_grouping_id: only for transformation_id = 'dimension_value_grouping'
                - event_type: optional int value only for transformed dimension with scope = 'product'
                  Allowed values:
                    Order: 9, Abandoned cart: 10, Product detail view: 22, Add to cart: 23, Remove from cart: 24

            date_from: Start date in YYYY-MM-DD format
            date_to: End date in YYYY-MM-DD format
            relative_date: Alternative to date_from/date_to. Options:
                today, yesterday, last_week, last_month, last_year, last_X_days
                last_X_days must be in range 1 <= X <= 365
                For periods beyond the last year use date_from and date_to

            filters: Optional dimension filter group with structure:
                {"operator": "and"|"or", "conditions": [...]}

                Each condition:
                {"column_id": "...", "condition": {"operator": "<op>", "value": ...}}

                Filter operators:
                - String: eq, neq, contains, not_contains, starts_with, ends_with, matches, not_matches
                - Numeric: gt, gte, lt, lte
                - Null checks: empty, not_empty

                Note: Some operators only work with specific data types.
                Check dimension/metric details for type compatibility before filtering.
            metric_filters: as arg 'filters' but for metrics
            offset: Rows to skip (default: 0)
            limit: Max rows to return (default: 100, max: 100000)
            order_by: List of [column_index, "asc"|"desc"] pairs

        ---

        Reference:
        - Dimension IDs: analytics_dimensions_list
        - Metric IDs: analytics_metrics_list
        - Dimension details (transformations, types): analytics_dimensions_details_list
        - Metric details (types): analytics_metrics_details_list
        """
        try:
            client = create_piwik_client()
            response = client.analytics.execute_query(
                website_id=website_id,
                columns=columns,
                date_from=date_from,
                date_to=date_to,
                relative_date=relative_date,
                filters=filters,
                metric_filters=metric_filters,
                offset=offset,
                limit=limit,
                order_by=order_by,
            )

            return QueryExecuteResponse(
                status="success",
                result=response,
                message=f"Query executed successfully. Returned {len(response.data)} rows.",
            )
        except Exception as e:
            raise RuntimeError(f"Failed to execute query: {str(e)}")

    @mcp.tool(annotations=ToolAnnotations(title="Piwik PRO: List Dimensions", readOnlyHint=True))
    def analytics_dimensions_list(website_id: str) -> DimensionsList:
        """
        List available dimensions for analytics queries.

        Returns all dimensions that can be used as columns in analytics_query_execute.
        To get details use `analytics_dimensions_details_list`
        The format of the response:
        ```
        {"dimensions": [{column_id: column_name}],
        "custom_channel_groupings": [{custom_channel_grouping_id: column_name}]}
        ```
        Args:
            website_id: UUID of the website/app to get dimensions for

        Returns:
            DimensionsList with all available dimensions and custom channel groupings
        """
        client = create_piwik_client()
        response = client.analytics.list_dimensions(website_id)

        dimensions = {}
        custom_channel_groupings = {}

        for d in response.root:
            if not d.column_meta.is_visible:
                continue
            column_name = d.column_meta.column_name
            if d.column_id == "custom_channel_grouping":
                custom_channel_groupings[d.custom_channel_grouping_id] = column_name
            elif d.column_id not in DEPRECATED_DIMENSIONS:
                dimensions[d.column_id] = column_name

        return DimensionsList(dimensions=dimensions, custom_channel_groupings=custom_channel_groupings)

    @mcp.tool(annotations=ToolAnnotations(title="Piwik PRO: List Metrics", readOnlyHint=True))
    def analytics_metrics_list(website_id: str) -> MetricsList:
        """
        List available metrics for analytics queries.

        Returns all metrics that can be used as columns in analytics_query_execute.
        The format of the response:
        ```
        {"metrics": [{metric_id: metric_name}], ...}, "calculated_metrics": [{calculated_metric_id: column_name}]
        ```

        Args:
            website_id: UUID of the website/app to get metrics for

        Returns:
            MetricsList with all available metrics
        """
        client = create_piwik_client()
        metrics, calculated_metrics = {}, {}
        for metric in client.analytics.list_metrics(website_id).root:
            if not metric.column_meta.is_visible:
                continue
            column_name = metric.column_meta.column_name
            if metric.column_id == "calculated_metric":
                calculated_metrics[metric.calculated_metric_id] = column_name
            elif metric.column_id not in DEPRECATED_METRICS:
                metrics[metric.column_id] = column_name

        return MetricsList(metrics=metrics, calculated_metrics=calculated_metrics)

    @mcp.tool(annotations=ToolAnnotations(title="Piwik PRO: List Dimensions Details", readOnlyHint=True))
    def analytics_dimensions_details_list(website_id: str, dimensions: list[str]) -> DimensionsDetailsList:
        """
        List details of provided dimensions.

        Args:
            website_id: UUID of the website/app to get dimensions for
            dimensions: list of dimension names

        Returns:
            The list of all available dimensions with details

        Important: Use enum_values object values instead of keys for queries.
        """
        client = create_piwik_client()
        regular_dimensions: list[DimensionColumnDefinition] = []
        custom_channel_groupings: list[ColumnDefinition] = []
        dimension_value_groupings: dict[str, list[DimensionValueGroupingItem]] = defaultdict(list)

        for dvg in client.analytics.list_dimension_value_groupings(website_id).results:
            dimension_value_groupings[dvg.column_id].append(dvg)

        for dimension in client.analytics.list_dimensions(website_id).root:
            if dimension.column_id == "custom_channel_grouping" and dimension.custom_channel_grouping_id in dimensions:
                custom_channel_groupings.append(dimension)
            elif dimension.column_id in dimensions:
                # Convert to DimensionColumnDefinition to support enum_values and transformations
                dim_with_enum = DimensionColumnDefinition(**dimension.model_dump())
                dim_with_enum.available_transformations = get_available_transformations(
                    dimension.column_id,
                    dimension.column_meta.column_type,
                    dimension_value_groupings[dimension.column_id],
                )
                regular_dimensions.append(dim_with_enum)

        # Fetch enum values for dimensions that have them
        for dimension in regular_dimensions:
            if dimension.column_id in DIMENSIONS_WITH_ENUMS:
                url = f"{DIMENSIONS_URL_PREFIX}{dimension.column_id}.json"
                enum_data = fetch_json_from_url(url)
                # Parse [[id, name], ...] format to {name: id}
                dimension.enum_values = {str(item[1]): item[0] for item in enum_data}

        return DimensionsDetailsList(
            dimensions=regular_dimensions, custom_channel_groupings=custom_channel_groupings
        ).model_dump(exclude_none=True)  # type: ignore

    @mcp.tool(annotations=ToolAnnotations(title="Piwik PRO: List Metrics Details", readOnlyHint=True))
    def analytics_metrics_details_list(website_id: str, metrics: list[str]) -> MetricsDetailsList:
        """
        List details of provided metrics.

        Returns all metrics that can be used as columns in analytics_query_execute.

        Args:
            website_id: UUID of the website/app to get metrics for
            metrics: list of metric names

        Returns:
            The list of all available metrics with details
        """
        client = create_piwik_client()
        regular_metrics, calculated_metrics = [], []
        for metric in client.analytics.list_metrics(website_id).root:
            if metric.column_id == "calculated_metric" and metric.calculated_metric_id in metrics:
                calculated_metrics.append(metric)
            elif metric.column_id in metrics:
                regular_metrics.append(metric)

        return MetricsDetailsList(metrics=regular_metrics, calculated_metrics=calculated_metrics).model_dump(
            exclude_none=True
        )  # type: ignore
