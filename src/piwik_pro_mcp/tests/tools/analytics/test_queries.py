"""Tests for Analytics Query MCP tools."""

from unittest.mock import Mock, patch

import pytest
from mcp.server.fastmcp.exceptions import ToolError

from piwik_pro_mcp.api.methods.analytics.models import (
    DimensionsListResponse,
    DimensionValueGroupingListResponse,
    MetricsListResponse,
    QueryResponse,
    QueryResponseMeta,
)


# Mock data for dimensions
def create_mock_dimensions():
    """Create mock dimensions data for testing."""
    return DimensionsListResponse.model_validate(
        [
            {
                "column_id": "source",
                "requires_events": False,
                "column_meta": {
                    "column_name": "Source",
                    "column_type": "str_nocase",
                    "column_category": ["Traffic"],
                    "is_internal": True,
                    "is_google_search": True,
                    "is_google_ads": True,
                    "is_visible": True,
                    "scope": "session",
                    "is_rtr_compatible": True,
                },
            },
            {
                "column_id": "medium",
                "requires_events": False,
                "column_meta": {
                    "column_name": "Medium",
                    "column_type": "str_nocase",
                    "column_category": ["Traffic"],
                    "is_internal": True,
                    "is_google_search": True,
                    "is_google_ads": True,
                    "is_visible": True,
                    "scope": "session",
                    "is_rtr_compatible": True,
                },
            },
            {
                "custom_channel_grouping_id": "custom-channel-grouping-1",
                "column_id": "custom_channel_grouping",
                "requires_events": False,
                "column_meta": {
                    "column_name": "Custom Channel Grouping Name",
                    "column_type": "str",
                    "column_category": ["Custom channel groupings"],
                    "is_internal": True,
                    "is_google_search": True,
                    "is_visible": True,
                    "source_dimensions": [
                        {
                            "column_id": "source",
                            "requires_events": False,
                            "column_meta": {
                                "column_name": "Source",
                                "column_type": "str_nocase",
                                "column_category": ["Traffic"],
                                "is_internal": True,
                                "is_google_search": True,
                                "is_google_ads": True,
                                "is_visible": True,
                                "scope": "session",
                                "is_rtr_compatible": True,
                            },
                        },
                        {
                            "column_id": "referrer_type",
                            "requires_events": False,
                            "column_meta": {
                                "column_name": "Channel",
                                "column_type": "str",
                                "column_category": ["Traffic"],
                                "is_internal": True,
                                "is_google_search": True,
                                "is_visible": True,
                                "scope": "session",
                                "is_rtr_compatible": True,
                            },
                        },
                    ],
                    "scope": "session",
                    "is_rtr_compatible": True,
                    "description": "Custom Channel Grouping Description",
                },
            },
            {
                "column_id": "not_visible",
                "requires_events": False,
                "column_meta": {
                    "column_name": "Not Visible",
                    "column_type": "str_nocase",
                    "is_visible": False,
                },
            },
        ]
    )


# Mock data for metrics
def create_mock_metrics():
    """Create mock metrics data for testing."""
    return MetricsListResponse.model_validate(
        [
            {
                "column_id": "visitors",
                "requires_events": False,
                "column_meta": {
                    "column_name": "Visitors",
                    "column_type": "int",
                    "column_category": ["Session"],
                    "is_internal": True,
                    "is_visible": True,
                    "scope": "session",
                    "is_rtr_compatible": True,
                },
            },
            {
                "column_id": "session_unique_page_views",
                "requires_events": False,
                "column_meta": {
                    "column_name": "Unique page views in session",
                    "column_type": "int",
                    "column_category": ["Session"],
                    "is_internal": True,
                    "is_visible": True,
                    "scope": "session",
                },
            },
            {
                "column_id": "calculated_metric",
                "calculated_metric_id": "custom-metric-1",
                "requires_events": False,
                "column_meta": {
                    "column_name": "Custom Metric Name",
                    "column_type": "float",
                    "column_category": ["Calculated Metrics"],
                    "is_internal": True,
                    "is_visible": True,
                    "source_metrics": [
                        {
                            "column_id": "events",
                            "requires_events": False,
                            "column_meta": {
                                "column_name": "Events",
                                "column_type": "int",
                                "column_category": ["Session"],
                                "is_internal": True,
                                "is_visible": True,
                                "scope": "session",
                                "is_rtr_compatible": True,
                            },
                        }
                    ],
                    "scope": "session",
                    "is_rtr_compatible": True,
                    "description": "Custom Metric Name Description",
                    "show_total_percentage": True,
                },
            },
            {
                "column_id": "not_visible",
                "requires_events": False,
                "column_meta": {
                    "column_name": "Not Visible",
                    "column_type": "str_nocase",
                    "is_visible": False,
                },
            },
        ]
    )


def create_mock_dvg():
    return DimensionValueGroupingListResponse.model_validate(
        {
            "count": 1,
            "results": [
                {
                    "id": "dvg-1",
                    "website_id": "test-app-id",
                    "name": "Paid / non-paid",
                    "author": {"email": "system@piwik.pro"},
                    "is_author": False,
                    "column_id": "source",
                    "column_meta": {
                        "column_name": "Source",
                        "column_type": "str_nocase",
                        "column_category": ["Traffic"],
                        "is_internal": True,
                        "is_google_search": True,
                        "is_google_ads": True,
                        "is_visible": True,
                        "scope": "session",
                        "is_rtr_compatible": True,
                    },
                    "visibility": "public",
                    "is_global": False,
                    "created_at": "2021-11-10T09:25:34.352000Z",
                    "updated_at": "2021-11-10T09:25:34.352000Z",
                }
            ],
        }
    )


# Mock data for query response
def create_mock_query_response():
    """Create mock query response for testing."""
    return QueryResponse(
        data=[["google", 150], ["direct", 100]],
        meta=QueryResponseMeta(columns=["source", "visitors"], count=2),
    )


class TestDimensionsList:
    """Tests for analytics_dimensions_list tool."""

    @pytest.fixture
    def mock_piwik_client(self):
        with patch("piwik_pro_mcp.tools.analytics.query.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            mock_instance.analytics.list_dimensions.return_value = create_mock_dimensions()
            yield mock_instance

    @pytest.mark.asyncio
    async def test_dimensions_list_functional(self, mcp_server, mock_piwik_client):
        """Returns DimensionsList with {column_id: column_name} mapping."""
        result = await mcp_server.call_tool(
            "analytics_dimensions_list",
            {"website_id": "test-app-id"},
        )

        assert isinstance(result, tuple) and len(result) == 2
        _, data = result
        assert "dimensions" in data
        assert data["dimensions"]["source"] == "Source"
        assert data["dimensions"]["medium"] == "Medium"
        mock_piwik_client.analytics.list_dimensions.assert_called_once_with("test-app-id")

    @pytest.mark.asyncio
    async def test_dimensions_list_filters_invisible(self, mcp_server, mock_piwik_client):
        """Only returns visible dimensions (is_visible=True)."""
        result = await mcp_server.call_tool(
            "analytics_dimensions_list",
            {"website_id": "test-app-id"},
        )

        _, data = result
        # Should have 2 visible dimensions, not the internal one
        assert len(data["dimensions"]) == 2
        assert "not_visible" not in data["dimensions"]
        assert "source" in data["dimensions"]
        assert "medium" in data["dimensions"]


class TestMetricsList:
    """Tests for analytics_metrics_list tool."""

    @pytest.fixture
    def mock_piwik_client(self):
        with patch("piwik_pro_mcp.tools.analytics.query.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            mock_instance.analytics.list_metrics.return_value = create_mock_metrics()
            yield mock_instance

    @pytest.mark.asyncio
    async def test_metrics_list_functional(self, mcp_server, mock_piwik_client):
        """Returns MetricsList with metrics and calculated_metrics."""
        result = await mcp_server.call_tool(
            "analytics_metrics_list",
            {"website_id": "test-app-id"},
        )

        assert isinstance(result, tuple) and len(result) == 2
        _, data = result
        assert "metrics" in data
        assert "calculated_metrics" in data
        assert data["metrics"]["visitors"] == "Visitors"
        assert data["metrics"]["session_unique_page_views"] == "Unique page views in session"
        mock_piwik_client.analytics.list_metrics.assert_called_once_with("test-app-id")

    @pytest.mark.asyncio
    async def test_metrics_list_separates_calculated(self, mcp_server, mock_piwik_client):
        """Correctly separates regular metrics from calculated metrics."""
        result = await mcp_server.call_tool(
            "analytics_metrics_list",
            {"website_id": "test-app-id"},
        )

        _, data = result
        # Regular metrics
        assert "visitors" in data["metrics"]
        assert "session_unique_page_views" in data["metrics"]
        # Calculated metrics use calculated_metric_id as key
        assert "custom-metric-1" in data["calculated_metrics"]
        assert data["calculated_metrics"]["custom-metric-1"] == "Custom Metric Name"

    @pytest.mark.asyncio
    async def test_metrics_list_filters_invisible(self, mcp_server, mock_piwik_client):
        """Only returns visible metrics."""
        result = await mcp_server.call_tool(
            "analytics_metrics_list",
            {"website_id": "test-app-id"},
        )

        _, data = result
        # Should have 2 visible regular metrics, not the internal one
        assert len(data["metrics"]) == 2
        assert "not_visible" not in data["metrics"]


class TestQueryExecute:
    """Tests for analytics_query_execute tool."""

    @pytest.fixture
    def mock_piwik_client(self):
        with patch("piwik_pro_mcp.tools.analytics.query.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            mock_instance.analytics.execute_query.return_value = create_mock_query_response()
            yield mock_instance

    @pytest.mark.asyncio
    async def test_query_execute_success(self, mcp_server, mock_piwik_client):
        """Returns QueryExecuteResponse with status 'success'."""
        result = await mcp_server.call_tool(
            "analytics_query_execute",
            {
                "website_id": "test-app-id",
                "columns": [{"column_id": "source"}, {"column_id": "visitors"}],
                "relative_date": "yesterday",
            },
        )

        assert isinstance(result, tuple) and len(result) == 2
        _, data = result
        assert data["status"] == "success"
        assert "result" in data
        assert len(data["result"]["data"]) == 2
        assert data["result"]["meta"]["count"] == 2

    @pytest.mark.asyncio
    async def test_query_execute_with_all_params(self, mcp_server, mock_piwik_client):
        """All parameters passed correctly to API."""
        filters = {
            "operator": "and",
            "conditions": [{"column_id": "source", "condition": {"operator": "eq", "value": "google"}}],
        }
        metric_filters = {
            "operator": "and",
            "conditions": [{"column_id": "google_ads_clicks", "condition": {"operator": "gt", "value": 1000}}],
        }

        result = await mcp_server.call_tool(
            "analytics_query_execute",
            {
                "website_id": "test-app-id",
                "columns": [{"column_id": "source"}, {"column_id": "visitors"}],
                "date_from": "2024-01-01",
                "date_to": "2024-01-31",
                "filters": filters,
                "metric_filters": metric_filters,
                "offset": 10,
                "limit": 50,
                "order_by": [[1, "desc"]],
            },
        )

        _, data = result
        assert data["status"] == "success"

        # Verify API was called with correct parameters
        mock_piwik_client.analytics.execute_query.assert_called_once_with(
            website_id="test-app-id",
            columns=[{"column_id": "source"}, {"column_id": "visitors"}],
            date_from="2024-01-01",
            date_to="2024-01-31",
            relative_date=None,
            filters=filters,
            metric_filters=metric_filters,
            offset=10,
            limit=50,
            order_by=[[1, "desc"]],
        )

    @pytest.mark.asyncio
    async def test_query_execute_error_handling(self, mcp_server, mock_piwik_client):
        """Wraps exceptions in ToolError with RuntimeError message."""
        mock_piwik_client.analytics.execute_query.side_effect = Exception("API error")

        with pytest.raises(ToolError, match="Failed to execute query: API error"):
            await mcp_server.call_tool(
                "analytics_query_execute",
                {
                    "website_id": "test-app-id",
                    "columns": [{"column_id": "source"}],
                    "relative_date": "today",
                },
            )


class TestDimensionsDetailsList:
    """Tests for analytics_dimensions_details_list tool."""

    @pytest.fixture
    def mock_piwik_client(self):
        with patch("piwik_pro_mcp.tools.analytics.query.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            mock_instance.analytics.list_dimensions.return_value = create_mock_dimensions()
            mock_instance.analytics.list_dimension_value_groupings.return_value = create_mock_dvg()
            yield mock_instance

    @pytest.mark.asyncio
    async def test_dimensions_details_list(self, mcp_server, mock_piwik_client):
        """Returns filtered dimension details."""
        result = await mcp_server.call_tool(
            "analytics_dimensions_details_list",
            {"website_id": "test-app-id", "dimensions": ["source", "medium"]},
        )

        assert isinstance(result, tuple) and len(result) == 2
        _, data = result
        assert "dimensions" in data
        assert len(data["dimensions"]) == 2

        # Verify dimension details are returned
        column_ids = [d["column_id"] for d in data["dimensions"]]
        assert "source" in column_ids
        assert "medium" in column_ids
        # Internal dimension should not be included (not in requested list)
        assert "not_visible" not in column_ids

    @pytest.mark.asyncio
    async def test_dimensions_details_list_with_custom_channel_grouping(self, mcp_server, mock_piwik_client):
        """Returns custom channel grouping details when requested by custom_channel_grouping_id."""
        result = await mcp_server.call_tool(
            "analytics_dimensions_details_list",
            {"website_id": "test-app-id", "dimensions": ["source", "custom-channel-grouping-1"]},
        )

        assert isinstance(result, tuple) and len(result) == 2
        _, data = result
        assert "dimensions" in data
        assert "custom_channel_groupings" in data
        assert len(data["dimensions"]) == 1
        assert len(data["custom_channel_groupings"]) == 1
        assert data["custom_channel_groupings"][0]["custom_channel_grouping_id"] == "custom-channel-grouping-1"

    @pytest.mark.asyncio
    async def test_dimensions_details_list_partial_match(self, mcp_server, mock_piwik_client):
        """Returns only dimensions that match the requested list."""
        result = await mcp_server.call_tool(
            "analytics_dimensions_details_list",
            {"website_id": "test-app-id", "dimensions": ["source", "nonexistent"]},
        )

        _, data = result
        assert len(data["dimensions"]) == 1
        assert data["dimensions"][0]["column_id"] == "source"

    @pytest.mark.asyncio
    async def test_dimensions_details_list_with_dimension_value_groupings(self, mcp_server, mock_piwik_client):
        """Returns dimension value grouping for available tranformations."""
        result = await mcp_server.call_tool(
            "analytics_dimensions_details_list",
            {"website_id": "test-app-id", "dimensions": ["source", "medium"]},
        )

        assert isinstance(result, tuple) and len(result) == 2
        _, data = result
        assert "dimensions" in data
        assert len(data["dimensions"]) == 2
        assert data["dimensions"][0]["available_transformations"]["dimension_to_metric"] == []
        assert data["dimensions"][0]["available_transformations"]["dimension_to_dimension"] == [
            {
                "transformation_id": "dimension_value_grouping",
                "result_type": "str_nocase",
                "dimension_value_grouping_id": "dvg-1",
                "dimension_value_grouping_name": "Paid / non-paid",
            }
        ]
        assert data["dimensions"][1]["available_transformations"] == {
            "dimension_to_metric": [],
            "dimension_to_dimension": [],
        }


class TestMetricsDetailsList:
    """Tests for analytics_metrics_details_list tool."""

    @pytest.fixture
    def mock_piwik_client(self):
        with patch("piwik_pro_mcp.tools.analytics.query.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            mock_instance.analytics.list_metrics.return_value = create_mock_metrics()
            yield mock_instance

    @pytest.mark.asyncio
    async def test_metrics_details_list(self, mcp_server, mock_piwik_client):
        """Returns filtered metric details."""
        result = await mcp_server.call_tool(
            "analytics_metrics_details_list",
            {"website_id": "test-app-id", "metrics": ["visitors", "session_unique_page_views"]},
        )

        assert isinstance(result, tuple) and len(result) == 2
        _, data = result
        assert "metrics" in data
        assert len(data["metrics"]) == 2

        # Verify metric details are returned
        column_ids = [m["column_id"] for m in data["metrics"]]
        assert "visitors" in column_ids
        assert "session_unique_page_views" in column_ids

    @pytest.mark.asyncio
    async def test_metrics_details_list_with_calculated(self, mcp_server, mock_piwik_client):
        """Returns calculated metric details when requested by calculated_metric_id."""
        result = await mcp_server.call_tool(
            "analytics_metrics_details_list",
            {"website_id": "test-app-id", "metrics": ["visitors", "custom-metric-1"]},
        )

        _, data = result
        assert "metrics" in data
        assert "calculated_metrics" in data
        assert len(data["metrics"]) == 1
        assert len(data["calculated_metrics"]) == 1
        assert data["calculated_metrics"][0]["calculated_metric_id"] == "custom-metric-1"
