"""Tests for container settings tool implementations."""

from unittest.mock import Mock, patch

import pytest
from mcp.server.fastmcp.exceptions import ToolError

from piwik_pro_mcp.api.methods.common import JsonApiResource
from piwik_pro_mcp.api.methods.container_settings.models import (
    ContainerSettingsListResponse,
    InstallationCodeResponse,
)


class TestContainerSettingsTools:
    @pytest.fixture
    def mock_piwik_client(self):
        with patch("piwik_pro_mcp.tools.container_settings.tools.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            yield mock_instance

    @pytest.mark.asyncio
    async def test_get_installation_code_functional(self, mcp_server, mock_piwik_client):
        mock_response = InstallationCodeResponse(
            data=JsonApiResource(
                id="ic-1",
                type="installation_code",
                attributes={"code": "<script>/* install */</script>"},
            )
        )
        mock_piwik_client.container_settings.get_installation_code.return_value = mock_response

        result = await mcp_server.call_tool("container_settings_get_installation_code", {"app_id": "app-123"})

        assert isinstance(result, tuple)
        _, data = result
        assert data["code"] == "<script>/* install */</script>"
        mock_piwik_client.container_settings.get_installation_code.assert_called_once_with("app-123")

    @pytest.mark.asyncio
    async def test_get_container_settings_functional(self, mcp_server, mock_piwik_client):
        mock_response = ContainerSettingsListResponse(
            data=[
                JsonApiResource(
                    id="s1",
                    type="setting",
                    attributes={"name": "tracking_domain", "value": "x"},
                )
            ]
        )
        mock_piwik_client.container_settings.get_app_settings.return_value = mock_response

        result = await mcp_server.call_tool("container_settings_list", {"app_id": "app-123"})

        assert isinstance(result, tuple)
        _, data = result
        assert len(data["data"]) == 1
        mock_piwik_client.container_settings.get_app_settings.assert_called_once_with("app-123")

    @pytest.mark.asyncio
    async def test_get_installation_code_error_handling(self, mcp_server):
        # No mocking fixture: will fail to create client in tests and raise ToolError
        with pytest.raises(ToolError):
            await mcp_server.call_tool("container_settings_get_installation_code", {"app_id": "app-err"})

    @pytest.mark.asyncio
    async def test_get_container_settings_client_error_mapping(self, mcp_server):
        with patch("piwik_pro_mcp.tools.container_settings.tools.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance

            def _raise(*args, **kwargs):
                raise Exception("boom")

            mock_instance.container_settings.get_app_settings.side_effect = _raise

            with pytest.raises(Exception) as exc_info:
                await mcp_server.call_tool("container_settings_list", {"app_id": "app-1"})
            assert "failed to get container settings" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_get_container_settings_multiple_items_shape_validation(self, mcp_server, mock_piwik_client):
        mock_response = ContainerSettingsListResponse(
            data=[
                JsonApiResource(id="s1", type="setting", attributes={"name": "tracking_domain", "value": "x"}),
                JsonApiResource(id="s2", type="setting", attributes={"name": "ui_apis_domain", "value": "y"}),
            ],
            meta={"total": 2},
        )
        mock_piwik_client.container_settings.get_app_settings.return_value = mock_response

        result = await mcp_server.call_tool("container_settings_list", {"app_id": "app-123"})

        assert isinstance(result, tuple)
        _, data = result
        assert len(data["data"]) == 2
        assert data.get("meta", {}).get("total") in (None, 2)  # meta may be present depending on model dump
