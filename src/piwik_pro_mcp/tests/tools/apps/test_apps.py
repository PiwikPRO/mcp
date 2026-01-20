"""Tests for app management tool implementations."""

from unittest.mock import Mock, patch

import pytest
from mcp.server.fastmcp.exceptions import ToolError


class TestUpdateAppRefactoredFunctional:
    """Functional tests for the refactored piwik_update_app tool through MCP."""

    @pytest.fixture
    def mock_piwik_client(self):
        """Mock the Piwik client for testing."""
        with patch("piwik_pro_mcp.tools.apps.tools.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            # Mock successful app update
            mock_instance.apps.update_app.return_value = None
            yield mock_instance

    @pytest.mark.asyncio
    async def test_apps_update_with_valid_json_attributes_functional(self, mcp_server, mock_piwik_client):
        """Test piwik_update_app with valid JSON attributes through MCP."""
        # Valid attributes dictionary
        attributes = {"name": "Updated App Name", "timezone": "America/New_York"}

        # Call the tool through MCP server
        result = await mcp_server.call_tool("apps_update", {"app_id": "app-123", "attributes": attributes})

        # Verify result is a tuple with content and structured data
        assert isinstance(result, tuple)
        assert len(result) == 2
        content_list, structured_data = result
        assert isinstance(content_list, list)
        assert len(content_list) == 1
        assert hasattr(content_list[0], "text")

        # Extract the response from the structured data
        response = structured_data

        # Verify the result
        assert response["status"] == "success"
        assert "name" in response["updated_fields"]
        assert "timezone" in response["updated_fields"]
        assert "Updated App Name" in response["message"] or "app-123" in response["message"]

        # Verify the client was called correctly
        mock_piwik_client.apps.update_app.assert_called_once()
        call_args = mock_piwik_client.apps.update_app.call_args
        assert call_args[1]["app_id"] == "app-123"
        assert call_args[1]["name"] == "Updated App Name"
        assert call_args[1]["timezone"] == "America/New_York"

    @pytest.mark.asyncio
    async def test_apps_update_with_empty_json_object_functional(self, mcp_server):
        """Test piwik_update_app with empty dictionary through MCP."""
        # Call the tool through MCP server with empty dictionary
        with pytest.raises(ToolError) as exc_info:
            await mcp_server.call_tool("apps_update", {"app_id": "app-123", "attributes": {}})

        # Verify error message
        assert "No update parameters provided" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_apps_update_with_invalid_json_functional(self, mcp_server):
        """Test piwik_update_app with invalid data type through MCP."""
        # Call the tool through MCP server with invalid data type
        with pytest.raises(ToolError) as exc_info:
            await mcp_server.call_tool("apps_update", {"app_id": "app-123", "attributes": "invalid string"})

        # Verify error message - should be a validation error about expecting dict
        assert "validation" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_apps_update_with_validation_error_functional(self, mcp_server):
        """Test piwik_update_app with JSON that fails validation through MCP."""
        # Dictionary with invalid field values
        attributes = {
            "name": "A" * 200,  # Too long name (max 90 chars)
            "timezone": "invalid_timezone",
        }

        # Call the tool through MCP server
        with pytest.raises(ToolError) as exc_info:
            await mcp_server.call_tool("apps_update", {"app_id": "app-123", "attributes": attributes})

        # Verify error message
        assert "Invalid attribute" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_apps_update_with_null_values_functional(self, mcp_server, mock_piwik_client):
        """Test piwik_update_app with null values in JSON through MCP."""
        # Dictionary with null values should be filtered out
        attributes = {"name": "Valid Name", "timezone": None, "currency": "USD"}

        # Call the tool through MCP server
        result = await mcp_server.call_tool("apps_update", {"app_id": "app-123", "attributes": attributes})

        # Verify result is a tuple with content and structured data
        assert isinstance(result, tuple)
        assert len(result) == 2
        content_list, structured_data = result
        assert isinstance(content_list, list)
        assert len(content_list) == 1
        assert hasattr(content_list[0], "text")

        # Extract the response from the structured data
        response = structured_data

        assert response["status"] == "success"
        assert "name" in response["updated_fields"]
        assert "currency" in response["updated_fields"]
        assert "timezone" not in response["updated_fields"]  # Should be filtered out

    @pytest.mark.asyncio
    async def test_apps_update_with_complex_fields_functional(self, mcp_server, mock_piwik_client):
        """Test piwik_update_app with complex field types like arrays through MCP."""
        # Dictionary with arrays and complex fields
        attributes = {"name": "Complex App", "urls": ["https://example.com", "https://test.com"], "gdpr": True}

        # Call the tool through MCP server
        result = await mcp_server.call_tool("apps_update", {"app_id": "app-123", "attributes": attributes})

        # Verify result is a tuple with content and structured data
        assert isinstance(result, tuple)
        assert len(result) == 2
        content_list, structured_data = result
        assert isinstance(content_list, list)
        assert len(content_list) == 1
        assert hasattr(content_list[0], "text")

        # Extract the response from the structured data
        response = structured_data

        assert response["status"] == "success"
        assert "name" in response["updated_fields"]
        assert "urls" in response["updated_fields"]
        assert "gdpr" in response["updated_fields"]

        # Verify arrays were passed correctly
        call_args = mock_piwik_client.apps.update_app.call_args
        assert call_args[1]["urls"] == ["https://example.com", "https://test.com"]
        assert call_args[1]["gdpr"] is True


class TestAppCrudFunctional:
    """Functional tests for app CRUD tools through MCP."""

    @pytest.fixture
    def mock_piwik_client(self):
        """Mock the Piwik client for app tools."""
        with patch("piwik_pro_mcp.tools.apps.tools.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            yield mock_instance

    @pytest.mark.asyncio
    async def test_apps_create_happy_path(self, mcp_server, mock_piwik_client):
        attributes = {
            "name": "My App",
            "urls": ["https://example.com"],
            "timezone": "UTC",
            "currency": "USD",
            "gdpr": True,
        }

        mock_piwik_client.apps.create_app.return_value = {
            "data": {
                "id": "app-xyz",
                "type": "app",
                "attributes": {
                    "name": "My App",
                    "urls": ["https://example.com"],
                    "timezone": "UTC",
                    "currency": "USD",
                    "gdpr": True,
                    "addedAt": "2024-01-01T00:00:00Z",
                    "updatedAt": "2024-01-01T00:00:00Z",
                },
            }
        }

        result = await mcp_server.call_tool("apps_create", {"attributes": attributes})

        assert isinstance(result, tuple) and len(result) == 2
        _, data = result
        assert data["id"] == "app-xyz"
        assert data["name"] == "My App"
        assert data["urls"] == ["https://example.com"]

        call_args = mock_piwik_client.apps.create_app.call_args
        assert call_args[1]["name"] == "My App"
        assert call_args[1]["urls"] == ["https://example.com"]
        assert call_args[1]["timezone"] == "UTC"
        assert call_args[1]["currency"] == "USD"
        assert call_args[1]["gdpr"] is True

    @pytest.mark.asyncio
    async def test_apps_create_validation_error(self, mcp_server, mock_piwik_client):
        # Missing required fields like name/urls should trigger validation error via model
        with pytest.raises(ToolError) as exc_info:
            await mcp_server.call_tool("apps_create", {"attributes": {"timezone": "UTC"}})

        assert "Invalid attribute" in str(exc_info.value) or "Validation error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_apps_get_happy_path(self, mcp_server, mock_piwik_client):
        mock_piwik_client.apps.get_app.return_value = {
            "data": {
                "id": "app-123",
                "type": "app",
                "attributes": {
                    "name": "Test App",
                    "urls": ["https://a"],
                    "appType": "web",
                    "timezone": "UTC",
                    "currency": "USD",
                    "gdpr": False,
                    "gdprDataAnonymization": False,
                    "realTimeDashboards": True,
                    "addedAt": "2024-01-01T00:00:00Z",
                    "updatedAt": "2024-01-02T00:00:00Z",
                },
            }
        }

        result = await mcp_server.call_tool("apps_get", {"app_id": "app-123"})

        assert isinstance(result, tuple) and len(result) == 2
        _, data = result
        assert data["id"] == "app-123"
        assert data["name"] == "Test App"
        assert data["urls"] == ["https://a"]
        assert data["app_type"] == "web"
        assert data["timezone"] == "UTC"
        assert data["currency"] == "USD"
        assert data["gdpr_enabled"] is False

        mock_piwik_client.apps.get_app.assert_called_once_with("app-123")

    @pytest.mark.asyncio
    async def test_apps_list_happy_path(self, mcp_server, mock_piwik_client):
        mock_piwik_client.apps.list_apps.return_value = {
            "data": [
                {
                    "id": "app-1",
                    "type": "app",
                    "attributes": {
                        "name": "A",
                        "addedAt": "2024-01-01T00:00:00Z",
                        "updatedAt": "2024-01-02T00:00:00Z",
                    },
                }
            ],
            "meta": {"total": 1},
        }

        result = await mcp_server.call_tool("apps_list", {"limit": 5, "offset": 0, "search": "A"})

        assert isinstance(result, tuple) and len(result) == 2
        _, data = result
        assert data["total"] == 1
        assert data["limit"] == 5
        assert data["offset"] == 0
        assert isinstance(data["apps"], list) and len(data["apps"]) == 1
        assert data["apps"][0]["id"] == "app-1"
        assert data["apps"][0]["name"] == "A"

        mock_piwik_client.apps.list_apps.assert_called_once()
        call_args = mock_piwik_client.apps.list_apps.call_args
        assert call_args[1]["limit"] == 5
        assert call_args[1]["offset"] == 0
        assert call_args[1]["search"] == "A"

    @pytest.mark.asyncio
    async def test_apps_list_default_values(self, mcp_server, mock_piwik_client):
        mock_piwik_client.apps.list_apps.return_value = {
            "data": [
                {
                    "id": "app-1",
                    "type": "app",
                    "attributes": {
                        "name": "A",
                        "addedAt": "2024-01-01T00:00:00Z",
                        "updatedAt": "2024-01-02T00:00:00Z",
                    },
                }
            ],
            "meta": {"total": 1},
        }

        result = await mcp_server.call_tool("apps_list", {"search": "A"})

        assert isinstance(result, tuple) and len(result) == 2
        _, data = result
        assert data["total"] == 1
        assert data["limit"] == 100
        assert data["offset"] == 0

        mock_piwik_client.apps.list_apps.assert_called_once()
        call_args = mock_piwik_client.apps.list_apps.call_args
        assert call_args[1]["limit"] == 100
        assert call_args[1]["offset"] == 0
        assert call_args[1]["search"] == "A"

    @pytest.mark.asyncio
    async def test_apps_delete_happy_path(self, mcp_server, mock_piwik_client):
        mock_piwik_client.apps.delete_app.return_value = None

        result = await mcp_server.call_tool("apps_delete", {"app_id": "app-123"})

        assert isinstance(result, tuple) and len(result) == 2
        _, data = result
        assert data["status"] == "success"
        assert "deleted" in data["message"].lower()

        mock_piwik_client.apps.delete_app.assert_called_once_with("app-123")
