"""Tests for Tag Manager version tools."""

from unittest.mock import Mock, patch

import pytest


class TestVersionsFunctional:
    @pytest.fixture
    def mock_piwik_client(self):
        with patch("piwik_pro_mcp.tools.tag_manager.versions.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            yield mock_instance

    @pytest.mark.asyncio
    async def test_versions_list_happy_path(self, mcp_server, mock_piwik_client):
        mock_piwik_client.tag_manager.list_versions.return_value = {
            "data": [
                {"id": "v1", "type": "version", "attributes": {"name": "Draft 1"}},
            ],
            "meta": {"total": 1},
        }

        result = await mcp_server.call_tool("versions_list", {"app_id": "app-1", "limit": 5, "offset": 0})

        assert isinstance(result, tuple) and len(result) == 2
        _, data = result
        assert data["meta"]["total"] == 1
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == "v1"

        call_args = mock_piwik_client.tag_manager.list_versions.call_args
        assert call_args[1]["app_id"] == "app-1"
        assert call_args[1]["limit"] == 5
        assert call_args[1]["offset"] == 0

    @pytest.mark.asyncio
    async def test_versions_get_draft_happy_path(self, mcp_server, mock_piwik_client):
        mock_piwik_client.tag_manager.get_draft_version.return_value = {
            "data": {"id": "v-draft", "type": "version", "attributes": {"name": "Draft"}}
        }

        result = await mcp_server.call_tool("versions_get_draft", {"app_id": "app-1"})

        assert isinstance(result, tuple) and len(result) == 2
        _, data = result
        assert data["data"]["id"] == "v-draft"
        mock_piwik_client.tag_manager.get_draft_version.assert_called_once_with("app-1")

    @pytest.mark.asyncio
    async def test_versions_get_published_happy_path(self, mcp_server, mock_piwik_client):
        mock_piwik_client.tag_manager.get_published_version.return_value = {
            "data": {"id": "v-pub", "type": "version", "attributes": {"name": "Published"}}
        }

        result = await mcp_server.call_tool("versions_get_published", {"app_id": "app-1"})

        assert isinstance(result, tuple) and len(result) == 2
        _, data = result
        assert data["data"]["id"] == "v-pub"
        mock_piwik_client.tag_manager.get_published_version.assert_called_once_with("app-1")

    @pytest.mark.asyncio
    async def test_versions_publish_draft_happy_path_async(self, mcp_server, mock_piwik_client):
        mock_piwik_client.tag_manager.publish_draft_version.return_value = {
            "data": {
                "id": "v-new",
                "type": "version",
                "relationships": {"operation": {"data": {"id": "op-1", "type": "operation"}}},
            }
        }

        result = await mcp_server.call_tool("versions_publish_draft", {"app_id": "app-1"})

        assert isinstance(result, tuple) and len(result) == 2
        _, data = result
        assert data["status"] == "success"
        assert data["version_info"]["version_id"] == "v-new"
        assert data["version_info"]["operation_id"] == "op-1"
        assert data["version_info"]["is_async"] is True

    @pytest.mark.asyncio
    async def test_versions_publish_draft_missing_relationships(self, mcp_server, mock_piwik_client):
        mock_piwik_client.tag_manager.publish_draft_version.return_value = {
            "data": {"id": "v-new", "type": "version", "attributes": {"name": "v"}}
        }

        result = await mcp_server.call_tool("versions_publish_draft", {"app_id": "app-1"})
        assert isinstance(result, tuple)
        _, data = result
        assert data["status"] == "success"
        assert data["version_info"]["version_id"] == "v-new"

    @pytest.mark.asyncio
    async def test_versions_publish_draft_happy_path_sync(self, mcp_server, mock_piwik_client):
        mock_piwik_client.tag_manager.publish_draft_version.return_value = None

        result = await mcp_server.call_tool("versions_publish_draft", {"app_id": "app-1"})

        assert isinstance(result, tuple) and len(result) == 2
        _, data = result
        assert data["status"] == "success"
        assert data["version_info"]["is_async"] is False

    @pytest.mark.asyncio
    async def test_version_calls_error_propagation_toolerror(self, mcp_server, mock_piwik_client):
        # Simulate client raising error; our tools wrap in RuntimeError -> ToolError at MCP boundary
        def raise_err(*args, **kwargs):
            raise RuntimeError("Failed to list versions: boom")

        # Patch the tool implementation entry to raise
        with patch("piwik_pro_mcp.tools.tag_manager.versions.list_versions", side_effect=raise_err):
            with pytest.raises(Exception) as exc_info:
                await mcp_server.call_tool("versions_list", {"app_id": "app-x"})

            assert "Failed to list versions" in str(exc_info.value)
