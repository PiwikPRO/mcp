"""Tests for variable management tool implementations."""

from unittest.mock import Mock, patch

import pytest


class TestVariableCreateFunctional:
    """Functional tests for variable creation tools through MCP."""

    @pytest.mark.asyncio
    async def test_variables_create_with_valid_json_attributes_functional(self, mcp_server):
        """Test piwik_create_variable with valid JSON attributes through MCP."""
        # Valid attributes dictionary
        attributes = {"name": "Test Variable", "variable_type": "constant"}

        # Mock the variable-specific create_piwik_client
        with patch("piwik_pro_mcp.tools.tag_manager.variables.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            mock_instance.tag_manager.create_variable.return_value = {
                "data": {
                    "id": "variable-123",
                    "type": "variable",
                    "attributes": {"name": "Test Variable", "template": "constant", "is_active": True},
                }
            }

            # Call the tool through MCP server
            result = await mcp_server.call_tool("variables_create", {"app_id": "app-123", "attributes": attributes})

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
            assert response["data"]["id"] == "variable-123"
            assert response["data"]["attributes"]["name"] == "Test Variable"

            # Verify the client was called correctly
            mock_instance.tag_manager.create_variable.assert_called_once()
            call_args = mock_instance.tag_manager.create_variable.call_args
            assert call_args[1]["app_id"] == "app-123"
            assert call_args[1]["name"] == "Test Variable"
            assert call_args[1]["variable_type"] == "constant"
            assert call_args[1].get("is_active") is None  # Not provided in attributes


class TestVariableUpdateFunctional:
    """Functional tests for variable update tools through MCP."""

    @pytest.mark.asyncio
    async def test_variables_update_with_none_response_functional(self, mcp_server):
        """Test piwik_update_variable handles None response (204 No Content) correctly."""
        # Valid attributes dictionary for update
        attributes = {"name": "Updated Variable", "value": "new_value"}

        # Mock the variable-specific create_piwik_client
        with patch("piwik_pro_mcp.tools.tag_manager.variables.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance

            # Mock update_variable to return None (204 No Content response)
            mock_instance.tag_manager.update_variable.return_value = None

            # Mock get_variable to return the updated variable data
            mock_instance.tag_manager.get_variable.return_value = {
                "data": {
                    "id": "variable-123",
                    "type": "variable",
                    "attributes": {
                        "name": "Updated Variable",
                        "template": "constant",
                        "is_active": True,
                        "value": "new_value",
                    },
                }
            }

            # Call the tool through MCP server
            result = await mcp_server.call_tool(
                "variables_update", {"app_id": "app-123", "variable_id": "variable-123", "attributes": attributes}
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
            assert response["data"]["id"] == "variable-123"
            assert response["data"]["attributes"]["name"] == "Updated Variable"
            assert response["data"]["attributes"]["value"] == "new_value"

            # Verify the client was called correctly
            mock_instance.tag_manager.update_variable.assert_called_once()
            mock_instance.tag_manager.get_variable.assert_called_once()

            # Verify update_variable was called with correct parameters
            update_call_args = mock_instance.tag_manager.update_variable.call_args
            assert update_call_args[1]["app_id"] == "app-123"
            assert update_call_args[1]["variable_id"] == "variable-123"
            assert update_call_args[1]["name"] == "Updated Variable"
            assert update_call_args[1]["value"] == "new_value"

            # Verify get_variable was called to fetch updated data
            get_call_args = mock_instance.tag_manager.get_variable.call_args
            assert get_call_args[1]["app_id"] == "app-123"
            assert get_call_args[1]["variable_id"] == "variable-123"

    @pytest.mark.asyncio
    async def test_variables_update_with_normal_response_functional(self, mcp_server):
        """Test piwik_update_variable handles normal response correctly."""
        # Valid attributes dictionary for update
        attributes = {"name": "Updated Variable", "value": "new_value"}

        # Mock the variable-specific create_piwik_client
        with patch("piwik_pro_mcp.tools.tag_manager.variables.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance

            # Mock update_variable to return normal response
            mock_instance.tag_manager.update_variable.return_value = {
                "data": {
                    "id": "variable-123",
                    "type": "variable",
                    "attributes": {
                        "name": "Updated Variable",
                        "template": "constant",
                        "is_active": True,
                        "value": "new_value",
                    },
                }
            }

            # Call the tool through MCP server
            result = await mcp_server.call_tool(
                "variables_update", {"app_id": "app-123", "variable_id": "variable-123", "attributes": attributes}
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
            assert response["data"]["id"] == "variable-123"
            assert response["data"]["attributes"]["name"] == "Updated Variable"
            assert response["data"]["attributes"]["value"] == "new_value"

            # Verify the client was called correctly
            mock_instance.tag_manager.update_variable.assert_called_once()
            # Should NOT call get_variable when update_variable returns data
            mock_instance.tag_manager.get_variable.assert_not_called()

            # Verify update_variable was called with correct parameters
            update_call_args = mock_instance.tag_manager.update_variable.call_args
            assert update_call_args[1]["app_id"] == "app-123"
            assert update_call_args[1]["variable_id"] == "variable-123"
            assert update_call_args[1]["name"] == "Updated Variable"
            assert update_call_args[1]["value"] == "new_value"


class TestVariableCopyFunctional:
    """Functional tests for variable copy tools through MCP."""

    @pytest.mark.asyncio
    async def test_variables_copy_same_app_minimal(self, mcp_server):
        with patch("piwik_pro_mcp.tools.tag_manager.variables.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            mock_instance.tag_manager.copy_variable.return_value = {
                "data": {
                    "id": "variable-new-123",
                    "type": "variable",
                    "attributes": {"name": "Var (copy)"},
                    "relationships": {"operation": {"data": {"id": "op-3", "type": "operation"}}},
                }
            }

            result = await mcp_server.call_tool(
                "variables_copy",
                {"app_id": "app-123", "variable_id": "var-abc", "name": "Var (copy)"},
            )

            assert isinstance(result, tuple) and len(result) == 2
            _, data = result
            assert data["resource_id"] == "variable-new-123"
            assert data["operation_id"] == "op-3"
            assert data["copied_into_app_id"] == "app-123"
            assert data["name"] == "Var (copy)"

            call_args = mock_instance.tag_manager.copy_variable.call_args
            assert call_args[1]["app_id"] == "app-123"
            assert call_args[1]["variable_id"] == "var-abc"
            assert call_args[1]["name"] == "Var (copy)"
            assert call_args[1]["target_app_id"] is None

    @pytest.mark.asyncio
    async def test_variables_copy_cross_app(self, mcp_server):
        with patch("piwik_pro_mcp.tools.tag_manager.variables.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            mock_instance.tag_manager.copy_variable.return_value = {
                "data": {
                    "id": "variable-new-999",
                    "type": "variable",
                    "relationships": {"operation": {"data": {"id": "op-33", "type": "operation"}}},
                }
            }

            result = await mcp_server.call_tool(
                "variables_copy",
                {"app_id": "app-a", "variable_id": "var-a", "target_app_id": "app-b"},
            )

            assert isinstance(result, tuple) and len(result) == 2
            _, data = result
            assert data["resource_id"] == "variable-new-999"
            assert data["operation_id"] == "op-33"
            assert data["copied_into_app_id"] == "app-b"

            call_args = mock_instance.tag_manager.copy_variable.call_args
            assert call_args[1]["target_app_id"] == "app-b"


class TestVariableCrudListGetDelete:
    @pytest.mark.asyncio
    async def test_variables_list_happy_path(self, mcp_server):
        with patch("piwik_pro_mcp.tools.tag_manager.variables.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            mock_instance.tag_manager.list_variables.return_value = {
                "data": [{"id": "var1", "type": "variable", "attributes": {"name": "Var 1"}}],
                "meta": {"total": 1},
            }

            result = await mcp_server.call_tool(
                "variables_list", {"app_id": "app-1", "limit": 10, "offset": 0, "filters": None}
            )

            assert isinstance(result, tuple) and len(result) == 2
            _, data = result
            assert data["meta"]["total"] == 1
            assert data["data"][0]["id"] == "var1"

            call_args = mock_instance.tag_manager.list_variables.call_args
            assert call_args[1]["app_id"] == "app-1"

    @pytest.mark.asyncio
    async def test_variables_get_happy_path(self, mcp_server):
        with patch("piwik_pro_mcp.tools.tag_manager.variables.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            mock_instance.tag_manager.get_variable.return_value = {
                "data": {"id": "var1", "type": "variable", "attributes": {"name": "Var 1"}}
            }

            result = await mcp_server.call_tool("variables_get", {"app_id": "app-1", "variable_id": "var1"})

            assert isinstance(result, tuple) and len(result) == 2
            _, data = result
            assert data["data"]["id"] == "var1"
            mock_instance.tag_manager.get_variable.assert_called_once_with("app-1", "var1")


class TestVariableValidationErrors:
    @pytest.mark.asyncio
    async def test_variables_create_validation_error(self, mcp_server):
        # Missing required fields
        with pytest.raises(Exception) as exc_info:
            await mcp_server.call_tool(
                "variables_create",
                {"app_id": "app-1", "attributes": {"name": "Var"}},
            )
        assert "invalid" in str(exc_info.value).lower() or "validation" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_variables_update_validation_error(self, mcp_server):
        with pytest.raises(Exception) as exc_info:
            await mcp_server.call_tool(
                "variables_update",
                {"app_id": "app-1", "variable_id": "v1", "attributes": "not-a-dict"},
            )
        assert "validation" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_variables_list_invalid_filters_validation(self, mcp_server):
        with pytest.raises(Exception) as exc_info:
            await mcp_server.call_tool("variables_list", {"app_id": "app-1", "filters": {"unknown": "x"}})
        assert "invalid" in str(exc_info.value).lower() or "filter" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_variables_update_empty_dict_error(self, mcp_server):
        with pytest.raises(Exception) as exc_info:
            await mcp_server.call_tool("variables_update", {"app_id": "app-1", "variable_id": "v1", "attributes": {}})
        assert "no editable fields" in str(exc_info.value).lower()
