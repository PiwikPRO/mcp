"""Tests for tag management tool implementations."""

import json
from unittest.mock import Mock, patch

import pytest


class TestTagCreateFunctional:
    """Functional tests for tag creation tools through MCP."""

    @pytest.fixture
    def mock_piwik_client(self):
        """Mock the Piwik client for testing."""
        with patch("piwik_pro_mcp.tools.tag_manager.tags.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            # Mock successful tag operations
            mock_instance.tag_manager.create_tag.return_value = {
                "data": {
                    "id": "tag-123",
                    "type": "tag",
                    "attributes": {"name": "Test Tag", "template": "custom_tag", "is_active": True},
                }
            }
            yield mock_instance

    @pytest.mark.asyncio
    async def test_tags_create_with_valid_json_attributes_functional(self, mcp_server, mock_piwik_client):
        """Test piwik_create_tag with valid JSON attributes through MCP."""
        # Valid attributes dictionary
        attributes = {"name": "Test Tag", "template": "custom_tag", "is_active": True}

        # Call the tool through MCP server
        result = await mcp_server.call_tool("tags_create", {"app_id": "app-123", "attributes": attributes})

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
        assert response["data"]["id"] == "tag-123"
        assert response["data"]["attributes"]["name"] == "Test Tag"

        # Verify the client was called correctly
        mock_piwik_client.tag_manager.create_tag.assert_called_once()
        call_args = mock_piwik_client.tag_manager.create_tag.call_args
        assert call_args[1]["app_id"] == "app-123"
        assert call_args[1]["name"] == "Test Tag"
        assert call_args[1]["template"] == "custom_tag"
        assert call_args[1]["is_active"] is True


class TestTagUpdateFunctional:
    """Functional tests for tag update tools through MCP."""

    @pytest.fixture
    def mock_piwik_client(self):
        """Mock the Piwik client for testing."""
        with patch("piwik_pro_mcp.tools.tag_manager.tags.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            # Mock successful Tag Manager update operations
            mock_instance.tag_manager.update_tag.return_value = {
                "data": {
                    "id": "tag-123",
                    "type": "tag",
                    "attributes": {"name": "Updated Tag", "template": "googleAnalytics", "is_active": True},
                }
            }
            yield mock_instance

    @pytest.mark.asyncio
    async def test_tags_update_with_valid_json_attributes_functional(self, mcp_server, mock_piwik_client):
        """Test piwik_update_tag with valid JSON attributes through MCP."""
        # Valid attributes dictionary
        attributes = {"name": "Updated Tag", "is_active": True}

        # Call the tool through MCP server
        result = await mcp_server.call_tool(
            "tags_update", {"app_id": "app-123", "tag_id": "tag-123", "attributes": attributes}
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
        assert "data" in response
        assert response["data"]["id"] == "tag-123"
        assert response["data"]["attributes"]["name"] == "Updated Tag"

        # Verify the client was called correctly
        mock_piwik_client.tag_manager.update_tag.assert_called_once()
        call_args = mock_piwik_client.tag_manager.update_tag.call_args
        assert call_args[1]["app_id"] == "app-123"
        assert call_args[1]["tag_id"] == "tag-123"
        assert call_args[1]["name"] == "Updated Tag"
        assert call_args[1]["is_active"] is True
        assert call_args[1].get("template") is None  # Not provided in attributes


class TestTagCopyFunctional:
    """Functional tests for tag copy tools through MCP."""

    @pytest.mark.asyncio
    async def test_tags_copy_same_app_minimal(self, mcp_server):
        """Copies a tag within the same app with minimal params."""
        with patch("piwik_pro_mcp.tools.tag_manager.tags.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            mock_instance.tag_manager.copy_tag.return_value = {
                "data": {
                    "id": "tag-new-123",
                    "type": "tag",
                    "relationships": {"operation": {"data": {"id": "op-1", "type": "operation"}}},
                }
            }

            result = await mcp_server.call_tool(
                "tags_copy", {"app_id": "app-123", "tag_id": "tag-abc", "name": "Tag (copy)"}
            )

            assert isinstance(result, tuple) and len(result) == 2
            _, data = result
            assert data["resource_id"] == "tag-new-123"
            assert data["resource_type"] == "tag"
            assert data["operation_id"] == "op-1"
            assert data["copied_into_app_id"] == "app-123"
            assert data["name"] == "Tag (copy)"
            assert data["with_triggers"] is False

            mock_instance.tag_manager.copy_tag.assert_called_once()
            call_args = mock_instance.tag_manager.copy_tag.call_args
            assert call_args[1]["app_id"] == "app-123"
            assert call_args[1]["tag_id"] == "tag-abc"
            assert call_args[1]["name"] == "Tag (copy)"
            assert call_args[1]["target_app_id"] is None
            assert call_args[1]["with_triggers"] is False

    @pytest.mark.asyncio
    async def test_tags_copy_cross_app_with_triggers(self, mcp_server):
        """Copies a tag to another app, including triggers."""
        with patch("piwik_pro_mcp.tools.tag_manager.tags.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            mock_instance.tag_manager.copy_tag.return_value = {
                "data": {
                    "id": "tag-new-999",
                    "type": "tag",
                    "relationships": {"operation": {"data": {"id": "op-9", "type": "operation"}}},
                }
            }

            result = await mcp_server.call_tool(
                "tags_copy",
                {
                    "app_id": "app-1",
                    "tag_id": "tag-1",
                    "target_app_id": "app-2",
                    "name": "Copied",
                    "with_triggers": True,
                },
            )

            assert isinstance(result, tuple) and len(result) == 2
            _, data = result
            assert data["resource_id"] == "tag-new-999"
            assert data["operation_id"] == "op-9"
            assert data["copied_into_app_id"] == "app-2"
            assert data["with_triggers"] is True

            call_args = mock_instance.tag_manager.copy_tag.call_args
            assert call_args[1]["target_app_id"] == "app-2"
            assert call_args[1]["with_triggers"] is True

    @pytest.mark.asyncio
    async def test_list_available_parameters_update_tag_functional(self, mcp_server):
        """Test that tools_parameters_get returns correct schema for update_tag."""
        result = await mcp_server.call_tool("tools_parameters_get", {"tool_name": "tags_update"})

        assert isinstance(result, list)
        assert len(result) == 1
        assert hasattr(result[0], "text")

        schema = result[0].text
        schema_dict = json.loads(schema)

        # Verify the schema structure
        assert isinstance(schema_dict, dict)
        assert "properties" in schema_dict
        assert "type" in schema_dict
        assert schema_dict["type"] == "object"
        assert schema_dict["title"] == "TagManagerUpdateAttributes"

        # Check for expected fields (all optional for update)
        properties = schema_dict["properties"]
        assert "name" in properties
        assert "template" in properties
        assert "is_active" in properties

        # Verify all fields have default null (since they're optional for updates)
        for field_name, field_schema in properties.items():
            assert "anyOf" in field_schema, f"Field '{field_name}' should use anyOf structure"
            assert field_schema["default"] is None, f"Field '{field_name}' should have default null"


class TestTagCrudListGetDelete:
    @pytest.mark.asyncio
    async def test_tags_list_happy_path(self, mcp_server):
        with patch("piwik_pro_mcp.tools.tag_manager.tags.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            mock_instance.tag_manager.list_tags.return_value = {
                "data": [{"id": "t1", "type": "tag", "attributes": {"name": "Tag 1"}}],
                "meta": {"total": 1},
            }

            result = await mcp_server.call_tool(
                "tags_list", {"app_id": "app-1", "limit": 10, "offset": 0, "filters": None}
            )

            assert isinstance(result, tuple) and len(result) == 2
            _, data = result
            assert data["meta"]["total"] == 1
            assert data["data"][0]["id"] == "t1"

            call_args = mock_instance.tag_manager.list_tags.call_args
            assert call_args[1]["app_id"] == "app-1"

    @pytest.mark.asyncio
    async def test_tags_get_happy_path(self, mcp_server):
        with patch("piwik_pro_mcp.tools.tag_manager.tags.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            mock_instance.tag_manager.get_tag.return_value = {
                "data": {"id": "t1", "type": "tag", "attributes": {"name": "Tag 1"}}
            }

            result = await mcp_server.call_tool("tags_get", {"app_id": "app-1", "tag_id": "t1"})

            assert isinstance(result, tuple) and len(result) == 2
            _, data = result
            assert data["data"]["id"] == "t1"
            mock_instance.tag_manager.get_tag.assert_called_once_with("app-1", "t1")

    @pytest.mark.asyncio
    async def test_tags_delete_happy_path(self, mcp_server):
        with patch("piwik_pro_mcp.tools.tag_manager.tags.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            mock_instance.tag_manager.delete_tag.return_value = None

            result = await mcp_server.call_tool("tags_delete", {"app_id": "app-1", "tag_id": "t1"})

            assert isinstance(result, tuple) and len(result) == 2
            _, data = result
            assert data["status"] == "success"
            mock_instance.tag_manager.delete_tag.assert_called_once_with("app-1", "t1")


class TestTagEdgeCases:
    @pytest.mark.asyncio
    async def test_tags_list_invalid_filters_validation(self, mcp_server):
        # Invalid filters should raise validation error from schema
        with pytest.raises(Exception) as exc_info:
            await mcp_server.call_tool(
                "tags_list", {"app_id": "app-1", "limit": 10, "offset": 0, "filters": {"unknown": 1}}
            )
        assert "invalid" in str(exc_info.value).lower() or "filter" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_tags_update_no_params_error(self, mcp_server):
        # Empty attributes and triggers left unchanged should error
        with pytest.raises(Exception) as exc_info:
            await mcp_server.call_tool(
                "tags_update",
                {"app_id": "app-1", "tag_id": "t1", "attributes": {}},
            )
        assert "no update parameters provided" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_tags_list_triggers_invalid_params(self, mcp_server):
        with patch("piwik_pro_mcp.tools.tag_manager.tags.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance

            def _raise(*args, **kwargs):
                raise Exception("bad request")

            mock_instance.tag_manager.get_tag_triggers.side_effect = _raise

            with pytest.raises(Exception) as exc_info:
                await mcp_server.call_tool(
                    "tags_list_triggers",
                    {"app_id": "app-1", "tag_id": "t1", "sort": "-unknown"},
                )
            assert "failed to get tag triggers" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_triggers_list_tags_not_found_mapping(self, mcp_server):
        with patch("piwik_pro_mcp.tools.tag_manager.tags.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance

            def _raise(*args, **kwargs):
                raise Exception("not found")

            mock_instance.tag_manager.get_trigger_tags.side_effect = _raise

            with pytest.raises(Exception) as exc_info:
                await mcp_server.call_tool(
                    "triggers_list_tags",
                    {"app_id": "app-1", "trigger_id": "tr1"},
                )
            s = str(exc_info.value).lower()
            assert "trigger" in s and "app" in s and ("not found" in s or "failed" in s)

    @pytest.mark.asyncio
    async def test_tags_update_204_fetches_latest(self, mcp_server):
        with patch("piwik_pro_mcp.tools.tag_manager.tags.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            # Update returns None (204), then get_tag returns updated payload
            mock_instance.tag_manager.update_tag.return_value = None
            mock_instance.tag_manager.get_tag.return_value = {
                "data": {"id": "t1", "type": "tag", "attributes": {"name": "Updated"}}
            }

            result = await mcp_server.call_tool(
                "tags_update", {"app_id": "app-1", "tag_id": "t1", "attributes": {"name": "Updated"}}
            )

            assert isinstance(result, tuple) and len(result) == 2
            _, data = result
            assert data["data"]["id"] == "t1"
            mock_instance.tag_manager.get_tag.assert_called_once_with(app_id="app-1", tag_id="t1")


class TestTagValidationErrors:
    @pytest.mark.asyncio
    async def test_tags_create_validation_error(self, mcp_server):
        with pytest.raises(Exception) as exc_info:
            await mcp_server.call_tool(
                "tags_create",
                {"app_id": "app-1", "attributes": {"template": "custom_tag"}},
            )
        assert "invalid" in str(exc_info.value).lower() or "validation" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_tags_update_validation_error(self, mcp_server):
        with pytest.raises(Exception) as exc_info:
            await mcp_server.call_tool(
                "tags_update",
                {"app_id": "app-1", "tag_id": "t1", "attributes": "not-a-dict"},
            )
        assert "validation" in str(exc_info.value).lower()
