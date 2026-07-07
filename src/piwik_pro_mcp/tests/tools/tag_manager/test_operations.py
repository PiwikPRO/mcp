"""Tests for Tag Manager operation tools."""

from unittest.mock import Mock, patch

import pytest

from piwik_pro_mcp.api.exceptions import NotFoundError


class TestOperationsFunctional:
    @pytest.fixture
    def mock_piwik_client(self):
        with patch("piwik_pro_mcp.tools.tag_manager.operations.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            yield mock_instance

    @pytest.mark.asyncio
    async def test_operations_get_happy_path(self, mcp_server, mock_piwik_client):
        mock_piwik_client.tag_manager.get_operation.return_value = {
            "data": {
                "id": "op-1",
                "type": "operation",
                "attributes": {
                    "state": "completed",
                    "operation_type": "import/version",
                    "parameters": {
                        "target_app_id": "app-2",
                        "source_version_id": "ver-1",
                    },
                    "summary": {
                        "tags": [],
                        "triggers": [],
                        "variables": [],
                    },
                },
            }
        }

        result = await mcp_server.call_tool(
            "operations_get",
            {"app_id": "app-1", "operation_id": "op-1"},
        )

        assert isinstance(result, tuple) and len(result) == 2
        _, data = result
        assert data["data"]["id"] == "op-1"
        assert data["data"]["attributes"]["state"] == "completed"
        assert data["data"]["attributes"]["operation_type"] == "import/version"
        assert data["data"]["attributes"]["parameters"]["target_app_id"] == "app-2"
        assert "summary" in data["data"]["attributes"]
        mock_piwik_client.tag_manager.get_operation.assert_called_once_with("app-1", "op-1")

    @pytest.mark.asyncio
    async def test_operations_get_not_found(self, mcp_server, mock_piwik_client):
        mock_piwik_client.tag_manager.get_operation.side_effect = NotFoundError("Operation not found")

        with pytest.raises(Exception, match="Operation with ID op-missing not found in app app-1"):
            await mcp_server.call_tool(
                "operations_get",
                {"app_id": "app-1", "operation_id": "op-missing"},
            )

    @pytest.mark.asyncio
    async def test_operations_get_unexpected_response_type(self, mcp_server, mock_piwik_client):
        mock_piwik_client.tag_manager.get_operation.return_value = None

        with pytest.raises(Exception, match="Unexpected response type from get_operation"):
            await mcp_server.call_tool(
                "operations_get",
                {"app_id": "app-1", "operation_id": "op-1"},
            )
