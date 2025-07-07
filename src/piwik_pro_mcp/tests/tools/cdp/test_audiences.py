"""Tests for CDP audience management tool implementations."""

from unittest.mock import Mock, patch

import pytest

from piwik_pro_mcp.api.exceptions import NotFoundError


class TestAudienceCreateFunctional:
    """Functional tests for audience creation tools through MCP."""

    @pytest.fixture
    def mock_piwik_client(self):
        """Mock the Piwik client for testing."""
        with patch("piwik_pro_mcp.tools.cdp.audiences.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            # Mock successful audience operations
            mock_instance.cdp.create_audience.return_value = {
                "id": "audience-123",
                "name": "Test Audience",
                "description": "Test description",
                "membership_duration_days": 30,
            }
            yield mock_instance

    @pytest.mark.asyncio
    async def test_audience_create_with_valid_json_attributes_functional(self, mcp_server, mock_piwik_client):
        """Test audiences_create with valid JSON attributes through MCP."""
        # Valid attributes dictionary
        attributes = {
            "name": "High-Value Customers",
            "description": "Customers with high lifetime value",
            "definition": {
                "operator": "and",
                "conditions": [
                    {
                        "operator": "or",
                        "conditions": [
                            {
                                "condition_type": "profile",
                                "column_id": "total_revenue",
                                "value_selector": "none",
                                "condition": {"operator": "gte", "value": 1000},
                            }
                        ],
                    }
                ],
            },
            "membership_duration_days": 90,
        }

        # Call the tool through MCP server
        result = await mcp_server.call_tool("audiences_create", {"app_id": "app-123", "attributes": attributes})

        # Verify result is a tuple with content and structured data
        assert isinstance(result, tuple)
        assert len(result) == 2
        content_list, structured_data = result
        assert isinstance(content_list, list)
        assert len(content_list) == 1
        assert hasattr(content_list[0], "text")

        # Extract the response from the structured data
        response = structured_data

        # Verify the result structure
        assert "status" in response
        assert response["status"] == "success"
        assert response.get("audience_id") == "audience-123"
        assert response.get("audience_name") == "Test Audience"

        # Verify the client was called correctly
        mock_piwik_client.cdp.create_audience.assert_called_once()
        call_args = mock_piwik_client.cdp.create_audience.call_args
        assert call_args[1]["app_id"] == "app-123"
        assert call_args[1]["name"] == "High-Value Customers"
        assert call_args[1]["description"] == "Customers with high lifetime value"
        assert call_args[1]["membership_duration_days"] == 90


class TestAudienceUpdateFunctional:
    """Functional tests for audience update tools through MCP."""

    @pytest.fixture
    def mock_piwik_client(self):
        """Mock the Piwik client for testing."""
        with patch("piwik_pro_mcp.tools.cdp.audiences.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            # Mock successful audience update operations
            mock_instance.cdp.update_audience.return_value = {
                "id": "audience-123",
                "name": "Updated Audience",
                "description": "Updated description",
                "membership_duration_days": 60,
            }
            # Mock audiences_get for fetching current values
            mock_instance.cdp.get_audience.return_value = {
                "id": "audience-123",
                "name": "Original Audience",
                "description": "Original description",
                "definition": {"operator": "and", "conditions": []},
                "membership_duration_days": 30,
            }
            yield mock_instance

    @pytest.mark.asyncio
    async def test_audience_update_with_valid_json_attributes_functional(self, mcp_server, mock_piwik_client):
        """Test audiences_update with valid JSON attributes through MCP."""
        # Valid attributes dictionary
        attributes = {"name": "Updated Audience", "membership_duration_days": 60}

        # Call the tool through MCP server
        result = await mcp_server.call_tool(
            "audiences_update", {"app_id": "app-123", "audience_id": "audience-123", "attributes": attributes}
        )

        # Verify result is a tuple with content and structured data
        assert isinstance(result, tuple)
        assert len(result) == 2
        content_list, structured_data = result
        assert isinstance(content_list, list)
        assert len(content_list) == 1
        assert hasattr(content_list[0], "text")

        # Extract the response from the structured data
        response = structured_data

        # Verify the result structure
        assert "status" in response
        assert response["status"] == "success"

        # Verify the client was called correctly
        mock_piwik_client.cdp.update_audience.assert_called_once()
        call_args = mock_piwik_client.cdp.update_audience.call_args
        assert call_args[1]["app_id"] == "app-123"
        assert call_args[1]["audience_id"] == "audience-123"
        assert call_args[1]["name"] == "Updated Audience"
        assert call_args[1]["membership_duration_days"] == 60


class TestAudienceListGetFunctional:
    """Functional tests for audience listing and retrieval tools through MCP."""

    @pytest.mark.asyncio
    async def test_audiences_list_happy_path(self, mcp_server):
        """Test audiences_list with successful response."""
        with patch("piwik_pro_mcp.tools.cdp.audiences.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            # API returns direct list of audience dictionaries
            mock_instance.cdp.list_audiences.return_value = [
                {
                    "id": "audience-1",
                    "name": "Audience 1",
                    "description": "First audience",
                    "membership_duration_days": 30,
                }
            ]

            result = await mcp_server.call_tool("audiences_list", {"app_id": "app-123"})

            assert isinstance(result, tuple) and len(result) == 2
            content_list, data = result
            assert data["audiences"][0]["id"] == "audience-1"
            assert data["total"] == 1

            call_args = mock_instance.cdp.list_audiences.call_args
            assert call_args[1]["app_id"] == "app-123"

    @pytest.mark.asyncio
    async def test_audience_get_happy_path(self, mcp_server):
        """Test audiences_get with successful response."""
        with patch("piwik_pro_mcp.tools.cdp.audiences.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            # API returns direct audience dictionary
            mock_instance.cdp.get_audience.return_value = {
                "id": "audience-1",
                "name": "Test Audience",
                "description": "Test description",
                "definition": {"operator": "and", "conditions": []},
                "membership_duration_days": 30,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "author": {"email": "test@example.com"},
                "is_author": True,
                "version": 1,
            }

            result = await mcp_server.call_tool("audiences_get", {"app_id": "app-123", "audience_id": "audience-1"})

            assert isinstance(result, tuple) and len(result) == 2
            content_list, data = result
            assert data["id"] == "audience-1"
            assert data["name"] == "Test Audience"
            assert data["description"] == "Test description"
            assert data["membership_duration_days"] == 30

            mock_instance.cdp.get_audience.assert_called_once_with(app_id="app-123", audience_id="audience-1")


class TestAudienceDeleteFunctional:
    """Functional tests for audience deletion tools through MCP."""

    @pytest.fixture
    def mock_piwik_client(self):
        """Mock the Piwik client for testing."""
        with patch("piwik_pro_mcp.tools.cdp.audiences.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            # Mock successful audience deletion
            mock_instance.cdp.delete_audience.return_value = None  # DELETE returns 204
            yield mock_instance

    @pytest.mark.asyncio
    async def test_audience_delete_success(self, mcp_server, mock_piwik_client):
        """Test audiences_delete with successful deletion through MCP."""
        result = await mcp_server.call_tool("audiences_delete", {"app_id": "app-123", "audience_id": "audience-123"})

        # Verify result is a tuple with content and structured data
        assert isinstance(result, tuple)
        assert len(result) == 2
        content_list, structured_data = result
        assert isinstance(content_list, list)
        assert len(content_list) == 1
        assert hasattr(content_list[0], "text")

        # Extract the response from the structured data
        response = structured_data

        # Verify the result structure
        assert "status" in response
        assert response["status"] == "success"
        assert "successfully deleted" in response["message"].lower()
        assert "audience-123" in response["message"]

        # Verify the client was called correctly
        mock_piwik_client.cdp.delete_audience.assert_called_once_with(app_id="app-123", audience_id="audience-123")

    @pytest.mark.asyncio
    async def test_audience_delete_not_found_error(self, mcp_server):
        """Test audience deletion when audience doesn't exist."""
        with patch("piwik_pro_mcp.tools.cdp.audiences.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance

            def _raise(*args, **kwargs):
                raise NotFoundError("audience not found")

            mock_instance.cdp.delete_audience.side_effect = _raise

            with pytest.raises(Exception) as exc_info:
                await mcp_server.call_tool(
                    "audiences_delete",
                    {"app_id": "app-1", "audience_id": "nonexistent"},
                )
            error_msg = str(exc_info.value).lower()
            assert "audience" in error_msg and "not found" in error_msg


class TestAudienceEdgeCases:
    """Tests for edge cases and error scenarios in audience management."""

    @pytest.mark.asyncio
    async def test_audience_create_validation_error(self, mcp_server):
        """Test audience creation with invalid attributes."""
        with pytest.raises(Exception) as exc_info:
            await mcp_server.call_tool(
                "audiences_create",
                {"app_id": "app-1", "attributes": {"name": "Test"}},  # Missing required fields
            )
        # Look for validation error indicators
        error_msg = str(exc_info.value).lower()
        assert "invalid attribute" in error_msg or "field required" in error_msg

    @pytest.mark.asyncio
    async def test_audience_update_empty_params_success(self, mcp_server):
        """Test audience update with empty attributes succeeds (no-op update)."""
        with patch("piwik_pro_mcp.tools.cdp.audiences.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            # Mock audiences_get for fetching current values
            mock_instance.cdp.get_audience.return_value = {
                "id": "audience-1",
                "name": "Original Audience",
                "description": "Original description",
                "definition": {"operator": "and", "conditions": []},
                "membership_duration_days": 30,
            }
            # Mock successful update
            mock_instance.cdp.update_audience.return_value = {
                "id": "audience-1",
                "name": "Original Audience",
            }

            result = await mcp_server.call_tool(
                "audiences_update",
                {"app_id": "app-1", "audience_id": "audience-1", "attributes": {}},
            )

            # Should succeed with empty updated_fields
            assert isinstance(result, tuple) and len(result) == 2
            _, data = result
            assert data["status"] == "success"
            assert data["updated_fields"] == []

    @pytest.mark.asyncio
    async def test_audience_get_not_found_error(self, mcp_server):
        """Test audience retrieval when audience doesn't exist."""
        with patch("piwik_pro_mcp.tools.cdp.audiences.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance

            def _raise(*args, **kwargs):
                raise Exception("audience not found")

            mock_instance.cdp.get_audience.side_effect = _raise

            with pytest.raises(Exception) as exc_info:
                await mcp_server.call_tool(
                    "audiences_get",
                    {"app_id": "app-1", "audience_id": "nonexistent"},
                )
            s = str(exc_info.value).lower()
            assert "audience" in s and ("not found" in s or "failed" in s)
