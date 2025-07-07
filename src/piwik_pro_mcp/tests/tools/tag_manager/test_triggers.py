"""Tests for trigger management tool implementations."""

from unittest.mock import Mock, patch

import pytest

from piwik_pro_mcp.api.exceptions import NotFoundError


class TestTriggerCreateFunctional:
    """Functional tests for trigger creation tools through MCP."""

    @pytest.mark.asyncio
    async def test_triggers_create_with_valid_json_attributes_functional(self, mcp_server):
        """Test piwik_create_trigger with valid JSON attributes through MCP."""
        # Valid attributes dictionary
        attributes = {"name": "Test Trigger", "trigger_type": "event", "is_active": False}

        # Mock the trigger-specific create_piwik_client
        with patch("piwik_pro_mcp.tools.tag_manager.triggers.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            mock_instance.tag_manager.create_trigger.return_value = {
                "data": {
                    "id": "trigger-123",
                    "type": "trigger",
                    "attributes": {"name": "Test Trigger", "trigger_type": "event", "is_active": False},
                }
            }

            # Call the tool through MCP server
            result = await mcp_server.call_tool("triggers_create", {"app_id": "app-123", "attributes": attributes})

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
            assert "data" in response
            assert response["data"]["id"] == "trigger-123"
            assert response["data"]["attributes"]["name"] == "Test Trigger"

            # Verify the client was called correctly
            mock_instance.tag_manager.create_trigger.assert_called_once()
            call_args = mock_instance.tag_manager.create_trigger.call_args
            assert call_args[1]["app_id"] == "app-123"
            assert call_args[1]["name"] == "Test Trigger"
            assert call_args[1]["trigger_type"] == "event"
            assert call_args[1]["is_active"] is False


class TestTriggerCopyFunctional:
    """Functional tests for trigger copy tools through MCP."""

    @pytest.mark.asyncio
    async def test_triggers_copy_same_app_minimal(self, mcp_server):
        with patch("piwik_pro_mcp.tools.tag_manager.triggers.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            mock_instance.tag_manager.copy_trigger.return_value = {
                "data": {
                    "id": "trigger-new-123",
                    "type": "trigger",
                    "attributes": {"name": "Trigger (copy)"},
                    "relationships": {"operation": {"data": {"id": "op-2", "type": "operation"}}},
                }
            }

            result = await mcp_server.call_tool(
                "triggers_copy",
                {"app_id": "app-123", "trigger_id": "trig-abc", "name": "Trigger (copy)"},
            )

            assert isinstance(result, tuple) and len(result) == 2
            _, data = result
            assert data["resource_id"] == "trigger-new-123"
            assert data["operation_id"] == "op-2"
            assert data["copied_into_app_id"] == "app-123"
            assert data["name"] == "Trigger (copy)"

            call_args = mock_instance.tag_manager.copy_trigger.call_args
            assert call_args[1]["app_id"] == "app-123"
            assert call_args[1]["trigger_id"] == "trig-abc"
            assert call_args[1]["name"] == "Trigger (copy)"
            assert call_args[1]["target_app_id"] is None

    @pytest.mark.asyncio
    async def test_triggers_copy_cross_app(self, mcp_server):
        with patch("piwik_pro_mcp.tools.tag_manager.triggers.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            mock_instance.tag_manager.copy_trigger.return_value = {
                "data": {
                    "id": "trigger-new-999",
                    "type": "trigger",
                    "relationships": {"operation": {"data": {"id": "op-22", "type": "operation"}}},
                }
            }

            result = await mcp_server.call_tool(
                "triggers_copy",
                {"app_id": "app-a", "trigger_id": "trig-a", "target_app_id": "app-b"},
            )

            assert isinstance(result, tuple) and len(result) == 2
            _, data = result
            assert data["resource_id"] == "trigger-new-999"
            assert data["operation_id"] == "op-22"
            assert data["copied_into_app_id"] == "app-b"

            call_args = mock_instance.tag_manager.copy_trigger.call_args
            assert call_args[1]["target_app_id"] == "app-b"


class TestTriggerCrudListGetDelete:
    @pytest.mark.asyncio
    async def test_triggers_list_happy_path(self, mcp_server):
        with patch("piwik_pro_mcp.tools.tag_manager.triggers.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            mock_instance.tag_manager.list_triggers.return_value = {
                "data": [{"id": "tr1", "type": "trigger", "attributes": {"name": "Tr 1"}}],
                "meta": {"total": 1},
            }

            result = await mcp_server.call_tool(
                "triggers_list", {"app_id": "app-1", "limit": 10, "offset": 0, "filters": None}
            )

            assert isinstance(result, tuple) and len(result) == 2
            _, data = result
            assert data["meta"]["total"] == 1
            assert data["data"][0]["id"] == "tr1"

            call_args = mock_instance.tag_manager.list_triggers.call_args
            assert call_args[1]["app_id"] == "app-1"

    @pytest.mark.asyncio
    async def test_triggers_get_happy_path(self, mcp_server):
        with patch("piwik_pro_mcp.tools.tag_manager.triggers.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            mock_instance.tag_manager.get_trigger.return_value = {
                "data": {"id": "tr1", "type": "trigger", "attributes": {"name": "Tr 1"}}
            }

            result = await mcp_server.call_tool("triggers_get", {"app_id": "app-1", "trigger_id": "tr1"})

            assert isinstance(result, tuple) and len(result) == 2
            _, data = result
            assert data["data"]["id"] == "tr1"
            mock_instance.tag_manager.get_trigger.assert_called_once_with("app-1", "tr1")


class TestTriggerValidationErrors:
    @pytest.mark.asyncio
    async def test_triggers_create_validation_error(self, mcp_server):
        # Missing required fields
        with pytest.raises(Exception) as exc_info:
            await mcp_server.call_tool(
                "triggers_create",
                {"app_id": "app-1", "attributes": {"name": "Only name"}},
            )
        # Message may mention missing 'trigger_type'
        msg = str(exc_info.value).lower()
        assert "invalid" in msg or "validation" in msg or "trigger_type" in msg

    @pytest.mark.asyncio
    async def test_triggers_list_invalid_filters_validation(self, mcp_server):
        with pytest.raises(Exception) as exc_info:
            await mcp_server.call_tool("triggers_list", {"app_id": "app-1", "filters": {"unknown": True}})
        assert "invalid" in str(exc_info.value).lower() or "filter" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_triggers_get_not_found_mapping(self, mcp_server):
        with patch("piwik_pro_mcp.tools.tag_manager.triggers.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance

            def _raise(*args, **kwargs):
                raise NotFoundError(status_code=404, message="not found", response_data={})

            mock_instance.tag_manager.get_trigger.side_effect = _raise

            with pytest.raises(Exception) as exc_info:
                await mcp_server.call_tool("triggers_get", {"app_id": "app-1", "trigger_id": "tr1"})
            assert "not found" in str(exc_info.value).lower()
