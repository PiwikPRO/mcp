"""
Tests for analytics custom dimensions tools with attributes-based interface.
"""

from unittest.mock import Mock, patch

import pytest

from piwik_pro_mcp.api.methods.analytics.models import CustomDimensionAttributes, CustomDimensionResource


class TestCustomDimensionsCrudFunctional:
    """Functional tests for custom dimensions CRUD operations with attributes-based interface."""

    @pytest.fixture
    def mock_piwik_client(self):
        """Create a mock Piwik client."""
        with patch("piwik_pro_mcp.tools.analytics.custom_dimensions.create_piwik_client") as mock:
            mock_instance = Mock()
            mock.return_value = mock_instance
            yield mock_instance

    @pytest.mark.asyncio
    async def test_custom_dimensions_create_session_scope(self, mcp_server, mock_piwik_client):
        """Test creating a session-scoped custom dimension with attributes."""
        # Mock API response
        mock_piwik_client.analytics.create_custom_dimension.return_value = Mock(
            model_dump=lambda: {
                "data": {
                    "id": "cd-123",
                    "type": "CustomDimension",
                    "attributes": {
                        "website_id": "site-1",
                        "name": "User Type",
                        "description": "Type of user",
                        "active": True,
                        "case_sensitive": False,
                        "scope": "session",
                        "slot": 1,
                        "tracking_id": 100,
                    },
                }
            }
        )

        result = await mcp_server.call_tool(
            "analytics_custom_dimensions_create",
            {
                "website_id": "site-1",
                "name": "User Type",
                "scope": "session",
                "description": "Type of user",
                "attributes": {
                    "active": True,
                    "case_sensitive": False,
                },
            },
        )

        # Verify response structure (MCP returns tuple: (content_list, metadata_dict))
        assert isinstance(result, tuple) and len(result) == 2
        _, metadata = result
        assert "result" in metadata
        response_data = metadata["result"]
        assert response_data["data"]["id"] == "cd-123"
        assert response_data["data"]["type"] == "CustomDimension"
        assert response_data["data"]["attributes"]["scope"] == "session"

        # Verify call was made with correct parameters
        mock_piwik_client.analytics.create_custom_dimension.assert_called_once()

    @pytest.mark.asyncio
    async def test_custom_dimensions_create_product_scope(self, mcp_server, mock_piwik_client):
        """Test creating a product custom dimension with attributes."""
        # Mock API response
        mock_piwik_client.analytics.create_product_custom_dimension.return_value = Mock(
            model_dump=lambda: {
                "data": {
                    "id": "pcd-789",
                    "type": "ProductCustomDimension",
                    "attributes": {
                        "website_id": "site-1",
                        "name": "Product Color",
                        "description": "Color of the product",
                        "slot": 3,
                        "created_at": "2025-01-01T00:00:00Z",
                        "updated_at": "2025-01-01T00:00:00Z",
                    },
                }
            }
        )

        result = await mcp_server.call_tool(
            "analytics_custom_dimensions_create",
            {
                "website_id": "site-1",
                "name": "Product Color",
                "scope": "product",
                "description": "Color of the product",
                "attributes": {
                    "slot": 3,
                },
            },
        )

        # Verify response structure (MCP returns tuple: (content_list, metadata_dict))
        assert isinstance(result, tuple) and len(result) == 2
        _, metadata = result
        response_data = metadata["result"]
        assert response_data["data"]["id"] == "pcd-789"
        assert response_data["data"]["type"] == "ProductCustomDimension"

        # Verify product API was called
        mock_piwik_client.analytics.create_product_custom_dimension.assert_called_once()

    @pytest.mark.asyncio
    async def test_custom_dimensions_list_filtered_by_session(self, mcp_server, mock_piwik_client):
        """Test listing custom dimensions filtered by session scope."""

        # Mock API response with properly structured Pydantic models
        mock_piwik_client.analytics.list_custom_dimensions.return_value = Mock(
            data=[
                CustomDimensionResource(
                    id="cd-1",
                    type="CustomDimension",
                    attributes=CustomDimensionAttributes(
                        website_id="site-1",
                        name="Session Dim",
                        scope="session",
                        active=True,
                        case_sensitive=False,
                    ),
                ),
                CustomDimensionResource(
                    id="cd-2",
                    type="CustomDimension",
                    attributes=CustomDimensionAttributes(
                        website_id="site-1",
                        name="Event Dim",
                        scope="event",
                        active=True,
                        case_sensitive=False,
                    ),
                ),
            ],
            meta={"total": 2},
            model_dump=lambda: {
                "data": [
                    {
                        "id": "cd-1",
                        "type": "CustomDimension",
                        "attributes": {
                            "scope": "session",
                            "name": "Session Dim",
                            "website_id": "site-1",
                            "active": True,
                            "case_sensitive": False,
                        },
                    },
                    {
                        "id": "cd-2",
                        "type": "CustomDimension",
                        "attributes": {
                            "scope": "event",
                            "name": "Event Dim",
                            "website_id": "site-1",
                            "active": True,
                            "case_sensitive": False,
                        },
                    },
                ],
                "meta": {"total": 2},
            },
        )

        result = await mcp_server.call_tool(
            "analytics_custom_dimensions_list",
            {
                "website_id": "site-1",
                "scope": "session",
                "limit": 10,
                "offset": 0,
            },
        )

        # Verify response structure (MCP returns tuple: (content_list, metadata_dict))
        assert isinstance(result, tuple) and len(result) == 2
        _, metadata = result
        response_data = metadata["result"]
        # Only session dimensions should be returned
        assert len(response_data["data"]) == 1
        assert response_data["data"][0]["attributes"]["scope"] == "session"

    @pytest.mark.asyncio
    async def test_custom_dimensions_list_product_scope(self, mcp_server, mock_piwik_client):
        """Test listing product custom dimensions."""
        # Mock API response
        mock_piwik_client.analytics.list_product_custom_dimensions.return_value = Mock(
            model_dump=lambda: {
                "data": [
                    {
                        "id": "pcd-1",
                        "type": "ProductCustomDimension",
                        "attributes": {
                            "name": "Product Dim 1",
                            "website_id": "site-1",
                            "slot": 1,
                        },
                    }
                ],
                "meta": {"total": 1},
            }
        )

        result = await mcp_server.call_tool(
            "analytics_custom_dimensions_list",
            {
                "website_id": "site-1",
                "scope": "product",
            },
        )

        # Verify response structure (MCP returns tuple: (content_list, metadata_dict))
        assert isinstance(result, tuple) and len(result) == 2
        _, metadata = result
        response_data = metadata["result"]
        assert len(response_data["data"]) == 1
        assert response_data["data"][0]["type"] == "ProductCustomDimension"

        # Verify product API was called
        mock_piwik_client.analytics.list_product_custom_dimensions.assert_called_once()

    @pytest.mark.asyncio
    async def test_custom_dimensions_get_session_scope(self, mcp_server, mock_piwik_client):
        """Test getting a specific session-scoped dimension."""
        # Mock API response
        mock_piwik_client.analytics.get_custom_dimension.return_value = Mock(
            model_dump=lambda: {
                "data": {
                    "id": "cd-123",
                    "type": "CustomDimension",
                    "attributes": {
                        "website_id": "site-1",
                        "name": "User Type",
                        "scope": "session",
                        "active": True,
                        "case_sensitive": False,
                    },
                }
            }
        )

        result = await mcp_server.call_tool(
            "analytics_custom_dimensions_get",
            {
                "dimension_id": "cd-123",
                "website_id": "site-1",
                "scope": "session",
            },
        )

        # Verify response structure (MCP returns tuple: (content_list, metadata_dict))
        assert isinstance(result, tuple) and len(result) == 2
        _, metadata = result
        response_data = metadata["result"]
        assert response_data["data"]["id"] == "cd-123"
        assert response_data["data"]["type"] == "CustomDimension"

        # Verify standard API was called
        mock_piwik_client.analytics.get_custom_dimension.assert_called_once_with(
            dimension_id="cd-123",
            website_id="site-1",
        )

    @pytest.mark.asyncio
    async def test_custom_dimensions_update_session_scope(self, mcp_server, mock_piwik_client):
        """Test updating a session-scoped dimension with attributes."""
        # Mock API response
        mock_piwik_client.analytics.update_custom_dimension.return_value = Mock(
            model_dump=lambda: {
                "data": {
                    "id": "cd-123",
                    "type": "CustomDimension",
                    "attributes": {
                        "website_id": "site-1",
                        "name": "Updated User Type",
                        "scope": "session",
                        "active": False,
                        "case_sensitive": True,
                    },
                }
            }
        )

        result = await mcp_server.call_tool(
            "analytics_custom_dimensions_update",
            {
                "dimension_id": "cd-123",
                "website_id": "site-1",
                "name": "Updated User Type",
                "scope": "session",
                "attributes": {
                    "active": False,
                    "case_sensitive": True,
                },
            },
        )

        # Verify response structure (MCP returns tuple: (content_list, metadata_dict))
        assert isinstance(result, tuple) and len(result) == 2
        _, metadata = result
        response_data = metadata["result"]
        assert response_data["data"]["id"] == "cd-123"
        assert response_data["data"]["attributes"]["active"] is False

        # Verify standard API was called
        mock_piwik_client.analytics.update_custom_dimension.assert_called_once()

    @pytest.mark.asyncio
    async def test_custom_dimensions_get_slots(self, mcp_server, mock_piwik_client):
        """Test getting slot availability statistics."""
        # Mock API response
        mock_piwik_client.analytics.get_custom_dimension_slots.return_value = Mock(
            model_dump=lambda: {
                "data": {
                    "type": "CustomDimensionStatistics",
                    "id": "site-1",
                    "attributes": {
                        "session": {"available": 50, "used": 5, "left": 45},
                        "event": {"available": 50, "used": 10, "left": 40},
                        "product": {"available": 20, "used": 3, "left": 17},
                    },
                }
            }
        )

        result = await mcp_server.call_tool(
            "analytics_custom_dimensions_get_slots",
            {
                "website_id": "site-1",
            },
        )

        # Verify response structure (MCP returns tuple: (content_list, metadata_dict))
        assert isinstance(result, tuple) and len(result) == 2
        _, metadata = result
        # Slots endpoint returns data directly, not nested under 'result'
        response_data = metadata.get("result", metadata)
        assert response_data["data"]["type"] == "CustomDimensionStatistics"
        assert response_data["data"]["attributes"]["session"]["available"] == 50
        assert response_data["data"]["attributes"]["event"]["used"] == 10
        assert response_data["data"]["attributes"]["product"]["left"] == 17

        # Verify API was called
        mock_piwik_client.analytics.get_custom_dimension_slots.assert_called_once_with(website_id="site-1")
