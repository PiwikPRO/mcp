"""Tests for CDP attribute listing tool implementations."""

from unittest.mock import Mock, patch

import pytest


class TestAttributesListFunctional:
    """Functional tests for attribute listing tools through MCP."""

    @pytest.fixture
    def mock_piwik_client(self):
        """Mock the Piwik client for testing."""
        with patch("piwik_pro_mcp.tools.cdp.attributes.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            # API returns direct list of attribute dictionaries
            mock_instance.cdp.list_attributes.return_value = [
                {
                    "column_id": "total_revenue",
                    "event_data_key": "analytics.goal_revenue",
                    "immutable": True,
                    "column_meta": {
                        "column_name": "Total revenue",
                        "column_type": "number",
                        "column_unit": "currency",
                        "column_category": ["Ecommerce"],
                        "analytics_column_id": "goal_revenue",
                        "analytics_transformation_id": "sum",
                        "value_selectors": ["none"],
                        "extractions": ["first", "last", "all"],
                        "aggregation": "sum",
                        "scope": "profile",
                    },
                },
                {
                    "column_id": "last_activity_time",
                    "event_data_key": "analytics.last_activity_time",
                    "immutable": True,
                    "column_meta": {
                        "column_name": "Last activity time",
                        "column_type": "datetime",
                        "column_category": ["User"],
                        "value_selectors": ["none"],
                        "extractions": ["first", "last"],
                        "aggregation": "last",
                        "scope": "profile",
                    },
                },
            ]
            yield mock_instance

    @pytest.mark.asyncio
    async def test_activations_attributes_list_comprehensive_response(self, mcp_server, mock_piwik_client):
        """Test activations_attributes_list with comprehensive response data."""
        result = await mcp_server.call_tool("activations_attributes_list", {"app_id": "app-123"})

        # Verify result is a tuple with content and structured data
        assert isinstance(result, tuple)
        assert len(result) == 2
        content_list, data = result
        assert isinstance(content_list, list)
        assert len(content_list) == 1
        assert hasattr(content_list[0], "text")

        # Verify data structure
        assert "attributes" in data
        assert "total" in data
        assert data["total"] == 2
        assert len(data["attributes"]) == 2

        # Verify first attribute (total_revenue)
        attr1 = data["attributes"][0]
        assert attr1["column_id"] == "total_revenue"
        assert attr1["column_name"] == "Total revenue"
        assert attr1["column_type"] == "number"
        assert attr1["column_unit"] == "currency"
        assert attr1["column_category"] == ["Ecommerce"]
        assert attr1["scope"] == "profile"
        assert attr1["immutable"] is True

        # Verify second attribute (last_activity_time)
        attr2 = data["attributes"][1]
        assert attr2["column_id"] == "last_activity_time"
        assert attr2["column_name"] == "Last activity time"
        assert attr2["column_type"] == "datetime"
        assert attr2["scope"] == "profile"

        # Verify the client was called correctly
        mock_piwik_client.cdp.list_attributes.assert_called_once_with(app_id="app-123")


class TestAttributesEdgeCases:
    """Tests for edge cases and error scenarios in attribute listing."""

    @pytest.mark.asyncio
    async def test_activations_attributes_list_api_error(self, mcp_server):
        """Test attributes listing when API returns error."""
        with patch("piwik_pro_mcp.tools.cdp.attributes.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance

            def _raise(*args, **kwargs):
                raise Exception("API connection error")

            mock_instance.cdp.list_attributes.side_effect = _raise

            with pytest.raises(Exception) as exc_info:
                await mcp_server.call_tool("activations_attributes_list", {"app_id": "app-1"})

            assert "api" in str(exc_info.value).lower() and "error" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_activations_attributes_list_empty_response(self, mcp_server):
        """Test attributes listing with empty response."""
        with patch("piwik_pro_mcp.tools.cdp.attributes.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            mock_instance.cdp.list_attributes.return_value = []

            result = await mcp_server.call_tool("activations_attributes_list", {"app_id": "empty-app"})

            assert isinstance(result, tuple) and len(result) == 2
            _, data = result
            assert data["attributes"] == []
            assert data["total"] == 0


class TestAttributesDifferentTypes:
    """Tests for different column types in attribute listing."""

    @pytest.mark.asyncio
    async def test_activations_attributes_list_different_column_types(self, mcp_server):
        """Test attributes listing with various column types."""
        with patch("piwik_pro_mcp.tools.cdp.attributes.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            mock_instance.cdp.list_attributes.return_value = [
                {
                    "column_id": "user_id",
                    "event_data_key": "analytics.user_id",
                    "immutable": True,
                    "column_meta": {
                        "column_name": "User ID",
                        "column_type": "string",
                        "value_selectors": ["first", "last", "any"],
                        "scope": "profile",
                    },
                },
                {
                    "column_id": "consent_analytics",
                    "event_data_key": "analytics.consent_analytics",
                    "immutable": True,
                    "column_meta": {
                        "column_name": "Consent to analytics",
                        "column_type": "bool",
                        "value_selectors": ["none"],
                        "scope": "profile",
                    },
                },
            ]

            result = await mcp_server.call_tool("activations_attributes_list", {"app_id": "app-456"})

            assert isinstance(result, tuple) and len(result) == 2
            _, data = result
            assert data["total"] == 2

            # Verify different column types are handled
            attributes = {attr["column_id"]: attr for attr in data["attributes"]}
            assert attributes["user_id"]["column_type"] == "string"
            assert attributes["consent_analytics"]["column_type"] == "bool"
