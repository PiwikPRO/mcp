"""Tests for Analytics Query API methods."""

import pytest

from piwik_pro_mcp.api.methods.analytics.api import AnalyticsAPI
from piwik_pro_mcp.api.methods.analytics.models import (
    DimensionsListResponse,
    MetricsListResponse,
    QueryRequest,
    QueryResponse,
)
from piwik_pro_mcp.tests.api.utils import _FakeClient

# Sample mock data for dimensions
MOCK_DIMENSIONS_DATA = [
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
]

# Sample mock data for metrics
MOCK_METRICS_DATA = [
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
]

# Sample mock data for query response
MOCK_QUERY_RESPONSE = {
    "data": [["google", 150], ["direct", 100]],
    "meta": {"columns": ["source", "visitors"], "count": 2},
}


class TestListDimensions:
    """Tests for list_dimensions method."""

    def test_list_dimensions_success(self):
        """Returns DimensionsListResponse with valid dimension data."""
        fake_client = _FakeClient(response=MOCK_DIMENSIONS_DATA)
        api = AnalyticsAPI(fake_client)

        result = api.list_dimensions("test-website-id")

        assert isinstance(result, DimensionsListResponse)
        assert len(result.root) == 2
        assert result.root[0].column_id == "source"
        assert result.root[0].column_meta.column_name == "Source"
        assert result.root[1].column_id == "medium"

    def test_list_dimensions_sends_correct_params(self):
        """Verifies website_id param and Accept: application/json header."""
        fake_client = _FakeClient(response=MOCK_DIMENSIONS_DATA)
        api = AnalyticsAPI(fake_client)

        api.list_dimensions("test-website-id")

        assert fake_client.last_get is not None
        assert fake_client.last_get["url"] == "/analytics/api/engine/dimensions/"
        assert fake_client.last_get["params"] == {"website_id": "test-website-id"}
        assert fake_client.last_get["headers"] == {"Accept": "application/json"}


class TestListMetrics:
    """Tests for list_metrics method."""

    def test_list_metrics_success(self):
        """Returns MetricsListResponse with valid metric data."""
        fake_client = _FakeClient(response=MOCK_METRICS_DATA)
        api = AnalyticsAPI(fake_client)

        result = api.list_metrics("test-website-id")

        assert isinstance(result, MetricsListResponse)
        assert len(result.root) == 2
        assert result.root[0].column_id == "visitors"
        assert result.root[0].column_meta.column_name == "Visitors"

    def test_list_metrics_sends_correct_params(self):
        """Verifies website_id param and Accept: application/json header."""
        fake_client = _FakeClient(response=MOCK_METRICS_DATA)
        api = AnalyticsAPI(fake_client)

        api.list_metrics("test-website-id")

        assert fake_client.last_get is not None
        assert fake_client.last_get["url"] == "/analytics/api/engine/metrics/"
        assert fake_client.last_get["params"] == {"website_id": "test-website-id"}
        assert fake_client.last_get["headers"] == {"Accept": "application/json"}


class TestExecuteQuery:
    """Tests for execute_query method."""

    def test_execute_query_with_absolute_dates(self):
        """Query with date_from/date_to works correctly."""
        fake_client = _FakeClient(response=MOCK_QUERY_RESPONSE)
        api = AnalyticsAPI(fake_client)

        result = api.execute_query(
            website_id="test-website-id",
            columns=[{"column_id": "source"}, {"column_id": "visitors"}],
            date_from="2024-01-01",
            date_to="2024-01-31",
        )

        assert isinstance(result, QueryResponse)
        assert len(result.data) == 2
        assert result.meta.count == 2
        assert result.meta.columns == ["source", "visitors"]

        # Verify request payload
        assert fake_client.last_post is not None
        payload = fake_client.last_post["data"]
        assert payload["website_id"] == "test-website-id"
        assert payload["date_from"] == "2024-01-01"
        assert payload["date_to"] == "2024-01-31"
        assert "relative_date" not in payload

    def test_execute_query_with_relative_date(self):
        """Query with relative_date works correctly."""
        fake_client = _FakeClient(response=MOCK_QUERY_RESPONSE)
        api = AnalyticsAPI(fake_client)

        result = api.execute_query(
            website_id="test-website-id",
            columns=[{"column_id": "source"}],
            relative_date="last_7_days",
        )

        assert isinstance(result, QueryResponse)

        # Verify request payload
        assert fake_client.last_post is not None
        payload = fake_client.last_post["data"]
        assert payload["relative_date"] == "last_7_days"
        assert "date_from" not in payload
        assert "date_to" not in payload

    def test_execute_query_with_filters(self):
        """Query with filter conditions works correctly."""
        fake_client = _FakeClient(response=MOCK_QUERY_RESPONSE)
        api = AnalyticsAPI(fake_client)

        filters = {
            "operator": "and",
            "conditions": [{"column_id": "source", "condition": {"operator": "eq", "value": "google"}}],
        }
        metric_filters = {
            "operator": "and",
            "conditions": [{"column_id": "google_ads_clicks", "condition": {"operator": "gt", "value": 1000}}],
        }

        result = api.execute_query(
            website_id="test-website-id",
            columns=[{"column_id": "visitors"}],
            relative_date="yesterday",
            filters=filters,
            metric_filters=metric_filters,
        )

        assert isinstance(result, QueryResponse)

        # Verify filters in payload
        assert fake_client.last_post is not None
        assert fake_client.last_post["data"]["filters"] == filters
        assert fake_client.last_post["data"]["metric_filters"] == metric_filters

    def test_execute_query_with_order_by(self):
        """Query with ordering works correctly."""
        fake_client = _FakeClient(response=MOCK_QUERY_RESPONSE)
        api = AnalyticsAPI(fake_client)

        result = api.execute_query(
            website_id="test-website-id",
            columns=[{"column_id": "source"}, {"column_id": "visitors"}],
            relative_date="today",
            order_by=[[1, "desc"]],
        )

        assert isinstance(result, QueryResponse)

        # Verify order_by in payload
        assert fake_client.last_post is not None
        payload = fake_client.last_post["data"]
        assert payload["order_by"] == [[1, "desc"]]

    def test_execute_query_validates_date_fields(self):
        """Validation error when both absolute and relative dates provided."""
        fake_client = _FakeClient(response=MOCK_QUERY_RESPONSE)
        api = AnalyticsAPI(fake_client)

        with pytest.raises(ValueError, match="Cannot use relative_date with date_from/date_to"):
            api.execute_query(
                website_id="test-website-id",
                columns=[{"column_id": "source"}],
                date_from="2024-01-01",
                date_to="2024-01-31",
                relative_date="yesterday",
            )

    def test_execute_query_requires_dates(self):
        """Validation error when no dates provided."""
        fake_client = _FakeClient(response=MOCK_QUERY_RESPONSE)
        api = AnalyticsAPI(fake_client)

        with pytest.raises(ValueError, match="Must provide either relative_date or both date_from and date_to"):
            api.execute_query(
                website_id="test-website-id",
                columns=[{"column_id": "source"}],
            )

    def test_execute_query_requires_both_absolute_dates(self):
        """Validation error when only one absolute date provided."""
        fake_client = _FakeClient(response=MOCK_QUERY_RESPONSE)
        api = AnalyticsAPI(fake_client)

        with pytest.raises(ValueError, match="Both date_from and date_to are required"):
            api.execute_query(
                website_id="test-website-id",
                columns=[{"column_id": "source"}],
                date_from="2024-01-01",
            )

    def test_execute_query_validates_relative_date_format(self):
        """Validation error for invalid relative_date format."""
        fake_client = _FakeClient(response=MOCK_QUERY_RESPONSE)
        api = AnalyticsAPI(fake_client)

        with pytest.raises(ValueError, match="Invalid relative_date"):
            api.execute_query(
                website_id="test-website-id",
                columns=[{"column_id": "source"}],
                relative_date="invalid_format",
            )

    def test_execute_query_validates_last_x_days_range(self):
        """Validation error when last_X_days is out of range."""
        fake_client = _FakeClient(response=MOCK_QUERY_RESPONSE)
        api = AnalyticsAPI(fake_client)

        with pytest.raises(ValueError, match="last_X_days requires X in range 1-365"):
            api.execute_query(
                website_id="test-website-id",
                columns=[{"column_id": "source"}],
                relative_date="last_400_days",
            )

    def test_execute_query_with_offset_and_limit(self):
        """Query with pagination parameters works correctly."""
        fake_client = _FakeClient(response=MOCK_QUERY_RESPONSE)
        api = AnalyticsAPI(fake_client)

        api.execute_query(
            website_id="test-website-id",
            columns=[{"column_id": "source"}],
            relative_date="today",
            offset=50,
            limit=25,
        )

        assert fake_client.last_post is not None
        payload = fake_client.last_post["data"]
        assert payload["offset"] == 50
        assert payload["limit"] == 25

    def test_execute_query_with_column_options(self):
        """Query with transformations works correctly."""
        fake_client = _FakeClient(response=MOCK_QUERY_RESPONSE)
        api = AnalyticsAPI(fake_client)

        result = api.execute_query(
            website_id="test-website-id",
            columns=[
                {"column_id": "calculated_metric", "calculated_metric_id": "some-uuid-1"},
                {"column_id": "custom_channel_grouping", "custom_channel_grouping_id": "some-uuid-2"},
                {
                    "column_id": "source_medium",
                    "transformation_id": "dimension_value_grouping",
                    "dimension_value_grouping_id": "some-uuid-3",
                },
                {"column_id": "product_name", "transformation_id": "unique_count", "event_type": 23},
            ],
            relative_date="today",
        )

        assert isinstance(result, QueryResponse)

        assert fake_client.last_post is not None
        payload = fake_client.last_post["data"]
        assert payload == {
            "website_id": "test-website-id",
            "columns": [
                {"column_id": "calculated_metric", "calculated_metric_id": "some-uuid-1"},
                {"column_id": "custom_channel_grouping", "custom_channel_grouping_id": "some-uuid-2"},
                {
                    "column_id": "source_medium",
                    "transformation_id": "dimension_value_grouping",
                    "dimension_value_grouping_id": "some-uuid-3",
                },
                {"column_id": "product_name", "transformation_id": "unique_count", "event_type": 23},
            ],
            "relative_date": "today",
            "offset": 0,
            "limit": 100,
        }


class TestQueryRequestValidation:
    """Tests for QueryRequest Pydantic model validation."""

    def test_query_request_validates_absolute_dates(self):
        """QueryRequest accepts valid absolute dates."""
        request = QueryRequest(
            website_id="test-id",
            columns=[{"column_id": "source"}],
            date_from="2024-01-01",
            date_to="2024-01-31",
        )
        assert request.date_from == "2024-01-01"
        assert request.date_to == "2024-01-31"

    def test_query_request_validates_relative_date_format(self):
        """QueryRequest accepts valid relative dates."""
        for relative_date in ["today", "yesterday", "last_week", "last_month", "last_year", "last_30_days"]:
            request = QueryRequest(
                website_id="test-id",
                columns=[{"column_id": "source"}],
                relative_date=relative_date,
            )
            assert request.relative_date == relative_date

    def test_query_request_rejects_mixed_dates(self):
        """QueryRequest rejects both absolute and relative dates."""
        with pytest.raises(ValueError, match="Cannot use relative_date with date_from/date_to"):
            QueryRequest(
                website_id="test-id",
                columns=[{"column_id": "source"}],
                date_from="2024-01-01",
                date_to="2024-01-31",
                relative_date="today",
            )

    def test_query_request_validates_last_x_days_range(self):
        """QueryRequest validates last_X_days range (1-365)."""
        # Valid range
        request = QueryRequest(
            website_id="test-id",
            columns=[{"column_id": "source"}],
            relative_date="last_365_days",
        )
        assert request.relative_date == "last_365_days"

        # Out of range
        with pytest.raises(ValueError, match="last_X_days requires X in range 1-365"):
            QueryRequest(
                website_id="test-id",
                columns=[{"column_id": "source"}],
                relative_date="last_0_days",
            )
