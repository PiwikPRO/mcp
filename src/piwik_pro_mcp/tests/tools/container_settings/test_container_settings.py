"""Tests for container settings tool implementations."""

import json
from typing import get_args
from unittest.mock import Mock, patch

import pytest
from mcp.server.fastmcp.exceptions import ToolError

from piwik_pro_mcp.api.exceptions import NotFoundError
from piwik_pro_mcp.api.methods.common import JsonApiResource
from piwik_pro_mcp.api.methods.container_settings.models import (
    ContainerSettingsListResponse,
    InstallationCodeResponse,
)
from piwik_pro_mcp.tools.container_settings.models import (
    CONTAINER_APP_SETTING_NAMES,
    CONTAINER_APP_SETTINGS,
    ContainerAppSetting,
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

    @pytest.mark.asyncio
    async def test_update_container_settings_happy_path(self, mcp_server, mock_piwik_client):
        mock_piwik_client.container_settings.update_app_settings.return_value = None

        result = await mcp_server.call_tool(
            "container_settings_app_update",
            {
                "app_id": "app-123",
                "attributes": {
                    "data": [
                        {
                            "id": "automatic_scroll_tracking",
                            "value": {"is_enabled": True, "thresholds": [25, 50, 75]},
                        },
                        {"id": "tracking_domain", "value": "analytics.example.com"},
                    ]
                },
            },
        )

        assert isinstance(result, tuple)
        _, data = result
        assert data["status"] == "success"
        assert data["updated_fields"] == ["automatic_scroll_tracking", "tracking_domain"]

        # The tool must transform each setting into a JSON:API resource object.
        mock_piwik_client.container_settings.update_app_settings.assert_called_once_with(
            "app-123",
            [
                {
                    "id": "automatic_scroll_tracking",
                    "type": "container/app/setting",
                    "attributes": {"value": {"is_enabled": True, "thresholds": [25, 50, 75]}},
                },
                {
                    "id": "tracking_domain",
                    "type": "container/app/setting",
                    "attributes": {"value": "analytics.example.com"},
                },
            ],
        )

    @pytest.mark.asyncio
    async def test_update_container_settings_empty_data(self, mcp_server, mock_piwik_client):
        # An empty ``data`` list is rejected by the schema (min_length=1).
        with pytest.raises(Exception):
            await mcp_server.call_tool(
                "container_settings_app_update",
                {"app_id": "app-123", "attributes": {"data": []}},
            )
        mock_piwik_client.container_settings.update_app_settings.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_container_settings_unknown_setting_rejected(self, mcp_server, mock_piwik_client):
        with pytest.raises(Exception):
            await mcp_server.call_tool(
                "container_settings_app_update",
                {"app_id": "app-123", "attributes": {"data": [{"id": "not_a_setting", "value": "x"}]}},
            )
        mock_piwik_client.container_settings.update_app_settings.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_container_settings_extra_value_field_rejected(self, mcp_server, mock_piwik_client):
        with pytest.raises(Exception):
            await mcp_server.call_tool(
                "container_settings_app_update",
                {
                    "app_id": "app-123",
                    "attributes": {"data": [{"id": "spa_tracking", "value": {"is_enabled": True, "extra": 1}}]},
                },
            )
        mock_piwik_client.container_settings.update_app_settings.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_container_settings_duplicate_thresholds_rejected(self, mcp_server, mock_piwik_client):
        # The backend requires unique thresholds (``uniqueItems: true``); the tool rejects duplicates.
        with pytest.raises(Exception):
            await mcp_server.call_tool(
                "container_settings_app_update",
                {
                    "app_id": "app-123",
                    "attributes": {
                        "data": [
                            {
                                "id": "automatic_scroll_tracking",
                                "value": {"is_enabled": True, "thresholds": [25, 25, 50]},
                            }
                        ]
                    },
                },
            )
        mock_piwik_client.container_settings.update_app_settings.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_container_settings_missing_data_key(self, mcp_server, mock_piwik_client):
        # A missing ``data`` key is rejected by the schema (field required).
        with pytest.raises(Exception):
            await mcp_server.call_tool(
                "container_settings_app_update",
                {"app_id": "app-123", "attributes": {}},
            )
        mock_piwik_client.container_settings.update_app_settings.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_container_settings_accepts_templated_path(self, mcp_server, mock_piwik_client):
        # The backend's ``format: path`` accepts templated values (its own documented example is
        # "/tracking/{{ app_id }}.js"); the tool must not reject them client-side.
        mock_piwik_client.container_settings.update_app_settings.return_value = None
        templated_path = "/tracking/{{ app_id }}.js"

        result = await mcp_server.call_tool(
            "container_settings_app_update",
            {"app_id": "app-123", "attributes": {"data": [{"id": "container_js_path", "value": templated_path}]}},
        )

        _, data = result
        assert data["status"] == "success"
        mock_piwik_client.container_settings.update_app_settings.assert_called_once_with(
            "app-123",
            [{"id": "container_js_path", "type": "container/app/setting", "attributes": {"value": templated_path}}],
        )

    @pytest.mark.asyncio
    async def test_update_container_settings_not_found(self, mcp_server, mock_piwik_client):
        mock_piwik_client.container_settings.update_app_settings.side_effect = NotFoundError("nope")

        with pytest.raises(Exception) as exc_info:
            await mcp_server.call_tool(
                "container_settings_app_update",
                {"app_id": "app-x", "attributes": {"data": [{"id": "spa_tracking", "value": {"is_enabled": False}}]}},
            )
        assert "App with ID app-x not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_container_setting_happy_path(self, mcp_server, mock_piwik_client):
        mock_piwik_client.container_settings.delete_app_setting.return_value = None

        result = await mcp_server.call_tool(
            "container_settings_app_delete",
            {"app_id": "app-123", "setting_name": "automatic_scroll_tracking"},
        )

        assert isinstance(result, tuple)
        _, data = result
        assert data["status"] == "success"
        mock_piwik_client.container_settings.delete_app_setting.assert_called_once_with(
            "app-123", "automatic_scroll_tracking"
        )

    @pytest.mark.asyncio
    async def test_delete_container_setting_unknown_name_rejected(self, mcp_server, mock_piwik_client):
        with pytest.raises(Exception) as exc_info:
            await mcp_server.call_tool(
                "container_settings_app_delete",
                {"app_id": "app-123", "setting_name": "not_a_setting"},
            )
        assert "Unknown container setting" in str(exc_info.value)
        mock_piwik_client.container_settings.delete_app_setting.assert_not_called()

    @pytest.mark.asyncio
    async def test_container_settings_update_schema_discoverable(self, mcp_server):
        result = await mcp_server.call_tool("tools_parameters_get", {"tool_name": "container_settings_app_update"})
        assert isinstance(result, list) and result and hasattr(result[0], "text")
        schema = json.loads(result[0].text)
        assert schema["type"] == "object"
        assert "data" in schema["properties"]

    @pytest.mark.asyncio
    async def test_update_tool_description_carries_routing_vocabulary(self, mcp_server):
        """The tool description must mention the settings + action verbs so prompts route here."""
        tools = await mcp_server.list_tools()
        tool = next(t for t in tools if t.name == "container_settings_app_update")
        description = (tool.description or "").lower()

        # Setting names users refer to
        for term in ["automatic_scroll_tracking", "spa_tracking", "tracking_domain"]:
            assert term in description, f"'{term}' missing from tool description"
        # Action verbs the prompts use
        for verb in ["enable", "disable", "turn on/off", "set"]:
            assert verb in description, f"'{verb}' missing from tool description"

    @pytest.mark.asyncio
    async def test_update_tool_description_routes_domain_and_path_customization(self, mcp_server):
        """Requests to customize container domains/paths must route here, so the description
        must frame the domain-like settings as serving Piwik PRO (Tag Manager) containers."""
        tools = await mcp_server.list_tools()
        tool = next(t for t in tools if t.name == "container_settings_app_update")
        description = (tool.description or "").lower()

        # All domain-like / serving settings must be named as customizable here.
        for term in [
            "fpc",
            "tracking_domain",
            "static_resources_domain",
            "ui_apis_domain",
            "container_js_path",
            "tracking_script_path",
            "tracking_endpoint_path",
        ]:
            assert term in description, f"'{term}' missing from tool description"
        # Routing vocabulary tying these settings to serving Piwik PRO containers.
        for phrase in ["domain", "path", "container", "first party collector"]:
            assert phrase in description, f"'{phrase}' missing from tool description"

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "prompt_intent,setting_item",
        [
            (
                "please enable automatic scroll tracking",
                {"id": "automatic_scroll_tracking", "value": {"is_enabled": True, "thresholds": [5, 50, 95]}},
            ),
            ("turn off spa tracking", {"id": "spa_tracking", "value": {"is_enabled": False}}),
            ("set up tracking domain to test.com", {"id": "tracking_domain", "value": "test.com"}),
        ],
    )
    async def test_representative_prompts_produce_valid_updates(
        self, mcp_server, mock_piwik_client, prompt_intent, setting_item
    ):
        """The payloads a model would build for these prompts validate and reach the API unchanged."""
        mock_piwik_client.container_settings.update_app_settings.return_value = None

        result = await mcp_server.call_tool(
            "container_settings_app_update",
            {"app_id": "app-123", "attributes": {"data": [setting_item]}},
        )

        assert isinstance(result, tuple)
        _, data = result
        assert data["status"] == "success"
        assert data["updated_fields"] == [setting_item["id"]]
        mock_piwik_client.container_settings.update_app_settings.assert_called_once_with(
            "app-123",
            [
                {
                    "id": setting_item["id"],
                    "type": "container/app/setting",
                    "attributes": {"value": setting_item["value"]},
                }
            ],
        )


class TestContainerSettingModels:
    def test_canonical_container_setting_names(self):
        """The authoritative map of which settings belong to Container Settings must not drift."""
        assert set(CONTAINER_APP_SETTING_NAMES) == {
            "automatic_scroll_tracking",
            "spa_tracking",
            "fpc",
            "tracking_domain",
            "static_resources_domain",
            "ui_apis_domain",
            "container_js_path",
            "tracking_script_path",
            "tracking_endpoint_path",
        }
        # Names are unique and derived from the registered classes.
        assert len(CONTAINER_APP_SETTING_NAMES) == len(set(CONTAINER_APP_SETTING_NAMES))
        assert len(CONTAINER_APP_SETTING_NAMES) == len(CONTAINER_APP_SETTINGS)

    def test_update_union_stays_in_sync_with_registry(self):
        """The discriminated union the MCP tool validates against must enumerate exactly the registry."""
        union = get_args(ContainerAppSetting)[0]
        union_members = get_args(union)
        assert set(union_members) == set(CONTAINER_APP_SETTINGS)
