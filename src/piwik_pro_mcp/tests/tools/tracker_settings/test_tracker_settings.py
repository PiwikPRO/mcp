"""Tests for tracker settings tool implementations."""

import json
from unittest.mock import Mock, patch

import pytest

from piwik_pro_mcp.api.exceptions import NotFoundError


class TestUpdateAppTrackerSettingsFunctional:
    """Functional tests for the refactored piwik_update_app_tracker_settings tool through MCP."""

    @pytest.fixture
    def mock_piwik_client(self):
        """Mock the Piwik client for testing."""
        with patch("piwik_pro_mcp.tools.tracker_settings.tools.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            # Mock successful tracker settings update
            mock_instance.tracker_settings.update_app_settings.return_value = None
            yield mock_instance

    @pytest.mark.asyncio
    async def test_tracker_settings_app_update_with_valid_json_attributes_functional(
        self, mcp_server, mock_piwik_client
    ):
        """Test piwik_update_app_tracker_settings with valid JSON attributes through MCP."""
        # Valid attributes dictionary
        attributes = {
            "anonymize_visitor_ip_level": 2,
            "excluded_ips": ["192.168.1.1", "10.0.0.1"],
            "exclude_crawlers": True,
            "session_max_duration_seconds": 3600,
        }

        # Call the tool through MCP server
        result = await mcp_server.call_tool(
            "tracker_settings_app_update", {"app_id": "app-123", "attributes": attributes}
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

        # Verify the result
        assert response["status"] == "success"
        assert "anonymize_visitor_ip_level" in response["updated_fields"]
        assert "excluded_ips" in response["updated_fields"]
        assert "exclude_crawlers" in response["updated_fields"]
        assert "session_max_duration_seconds" in response["updated_fields"]

        # Verify the client was called correctly
        mock_piwik_client.tracker_settings.update_app_settings.assert_called_once()
        call_args = mock_piwik_client.tracker_settings.update_app_settings.call_args
        assert call_args[0][0] == "app-123"  # First positional argument
        assert call_args[1]["anonymize_visitor_ip_level"] == 2
        assert call_args[1]["excluded_ips"] == ["192.168.1.1", "10.0.0.1"]
        assert call_args[1]["exclude_crawlers"] is True
        assert call_args[1]["session_max_duration_seconds"] == 3600

    @pytest.mark.asyncio
    async def test_tracker_settings_app_get_happy_path(self, mcp_server, mock_piwik_client):
        mock_piwik_client.tracker_settings.get_app_settings.return_value = {
            "data": {"attributes": {"excluded_ips": ["1.1.1.1"], "exclude_crawlers": True}}
        }

        result = await mcp_server.call_tool("tracker_settings_app_get", {"app_id": "app-1"})

        assert isinstance(result, tuple)
        _, data = result
        assert data["excluded_ips"] == ["1.1.1.1"]
        assert data["exclude_crawlers"] is True
        mock_piwik_client.tracker_settings.get_app_settings.assert_called_once_with("app-1")

    @pytest.mark.asyncio
    async def test_list_available_parameters_update_app_tracker_settings_functional(self, mcp_server):
        """Test that list_available_parameters returns correct schema for update_app_tracker_settings."""
        # Call the tool through MCP server
        result = await mcp_server.call_tool("tools_parameters_get", {"tool_name": "tracker_settings_app_update"})

        # Verify result is a list of content blocks (success case)
        assert isinstance(result, list)
        assert len(result) == 1
        assert hasattr(result[0], "text")

        # Extract the schema from the result
        schema = result[0].text
        schema_dict = json.loads(schema)

        # Verify the schema structure
        assert isinstance(schema_dict, dict)
        assert "properties" in schema_dict
        assert "type" in schema_dict
        assert schema_dict["type"] == "object"
        assert schema_dict["title"] == "AppTrackerSettings"

        # Check for specific expected fields from AppTrackerSettingsV2
        properties = schema_dict["properties"]
        assert "anonymize_visitor_ip_level" in properties
        assert "excluded_ips" in properties
        assert "exclude_crawlers" in properties
        assert "session_max_duration_seconds" in properties
        assert "anonymize_visitor_geolocation_level" in properties

        # Verify all fields are optional (use anyOf structure)
        for field_name, field_schema in properties.items():
            if field_name != "updated_at":  # Skip system field
                assert "anyOf" in field_schema, f"Field '{field_name}' should use anyOf structure"
                assert field_schema["default"] is None, f"Field '{field_name}' should have default null"

        # Verify specific field types
        assert properties["anonymize_visitor_ip_level"]["anyOf"][0]["type"] == "integer"
        assert properties["excluded_ips"]["anyOf"][0]["type"] == "array"
        assert properties["exclude_crawlers"]["anyOf"][0]["type"] == "boolean"
        assert properties["session_max_duration_seconds"]["anyOf"][0]["type"] == "integer"

        # Verify field descriptions exist
        assert "description" in properties["anonymize_visitor_ip_level"]
        assert "description" in properties["excluded_ips"]


class TestUpdateGlobalTrackerSettingsFunctional:
    """Functional tests for the refactored piwik_update_global_tracker_settings tool through MCP."""

    @pytest.fixture
    def mock_piwik_client(self):
        """Mock the Piwik client for testing."""
        with patch("piwik_pro_mcp.tools.tracker_settings.tools.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            # Mock successful global tracker settings update
            mock_instance.tracker_settings.update_global_settings.return_value = None
            yield mock_instance

    @pytest.mark.asyncio
    async def test_tracker_settings_global_update_with_valid_json_attributes_functional(
        self, mcp_server, mock_piwik_client
    ):
        """Test piwik_update_global_tracker_settings with valid JSON attributes through MCP."""
        # Valid attributes dictionary
        attributes = {
            "anonymize_visitor_ip_level": 2,
            "excluded_ips": ["192.168.1.1", "10.0.0.1"],
            "excluded_url_params": ["utm_source", "utm_medium"],
            "visitor_geolocation_based_on_anonymized_ip": True,
        }

        # Call the tool through MCP server
        result = await mcp_server.call_tool("tracker_settings_global_update", {"attributes": attributes})

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
        assert "anonymize_visitor_ip_level" in response["updated_fields"]
        assert "excluded_ips" in response["updated_fields"]
        assert "excluded_url_params" in response["updated_fields"]
        assert "visitor_geolocation_based_on_anonymized_ip" in response["updated_fields"]

        # Verify the client was called correctly
        mock_piwik_client.tracker_settings.update_global_settings.assert_called_once()
        call_args = mock_piwik_client.tracker_settings.update_global_settings.call_args
        assert call_args[1]["anonymize_visitor_ip_level"] == 2
        assert call_args[1]["excluded_ips"] == ["192.168.1.1", "10.0.0.1"]
        assert call_args[1]["excluded_url_params"] == ["utm_source", "utm_medium"]
        assert call_args[1]["visitor_geolocation_based_on_anonymized_ip"] is True

    @pytest.mark.asyncio
    async def test_list_available_parameters_update_global_tracker_settings_functional(self, mcp_server):
        """Test that list_available_parameters returns correct schema for update_global_tracker_settings."""
        # Call the tool through MCP server
        result = await mcp_server.call_tool("tools_parameters_get", {"tool_name": "tracker_settings_global_update"})

        # Verify result is a list of content blocks (success case)
        assert isinstance(result, list)
        assert len(result) == 1
        assert hasattr(result[0], "text")

        # Extract the schema from the result
        schema = result[0].text
        schema_dict = json.loads(schema)

        # Verify the schema structure
        assert isinstance(schema_dict, dict)
        assert "properties" in schema_dict
        assert "type" in schema_dict
        assert schema_dict["type"] == "object"
        assert schema_dict["title"] == "GlobalTrackerSettings"

        # Check for specific expected fields from GlobalTrackerSettingsV1
        properties = schema_dict["properties"]
        assert "anonymize_visitor_ip_level" in properties
        assert "excluded_ips" in properties
        assert "excluded_url_params" in properties
        assert "excluded_user_agents" in properties
        assert "site_search_query_params" in properties
        assert "site_search_category_params" in properties
        assert "visitor_geolocation_based_on_anonymized_ip" in properties

        # Verify all fields are optional (use anyOf structure)
        for field_name, field_schema in properties.items():
            if field_name != "updated_at":  # Skip system field
                assert "anyOf" in field_schema, f"Field '{field_name}' should use anyOf structure"
                assert field_schema["default"] is None, f"Field '{field_name}' should have default null"

        # Verify specific field types
        assert properties["anonymize_visitor_ip_level"]["anyOf"][0]["type"] == "integer"
        assert properties["excluded_ips"]["anyOf"][0]["type"] == "array"
        assert properties["excluded_url_params"]["anyOf"][0]["type"] == "array"
        assert properties["visitor_geolocation_based_on_anonymized_ip"]["anyOf"][0]["type"] == "boolean"

        # Verify field descriptions exist
        assert "description" in properties["anonymize_visitor_ip_level"]
        assert "description" in properties["excluded_ips"]
        assert "description" in properties["excluded_url_params"]
        assert "description" in properties["visitor_geolocation_based_on_anonymized_ip"]

    @pytest.mark.asyncio
    async def test_tracker_settings_global_get_happy_path(self, mcp_server, mock_piwik_client):
        mock_piwik_client.tracker_settings.get_global_settings.return_value = {
            "data": {"attributes": {"excluded_ips": ["2.2.2.2"], "excluded_url_params": ["utm_source"]}}
        }

        result = await mcp_server.call_tool("tracker_settings_global_get", {})

        assert isinstance(result, tuple)
        _, data = result
        assert data["excluded_ips"] == ["2.2.2.2"]
        assert data["excluded_url_params"] == ["utm_source"]
        mock_piwik_client.tracker_settings.get_global_settings.assert_called_once()

    @pytest.mark.asyncio
    async def test_tracker_settings_app_delete_happy_path(self, mcp_server, mock_piwik_client):
        mock_piwik_client.tracker_settings.delete_app_setting.return_value = None

        result = await mcp_server.call_tool(
            "tracker_settings_app_delete", {"app_id": "app-1", "setting": "excluded_ips"}
        )

        assert isinstance(result, tuple)
        _, data = result
        assert data["status"] == "success"
        mock_piwik_client.tracker_settings.delete_app_setting.assert_called_once_with("app-1", "excluded_ips")

    @pytest.mark.asyncio
    async def test_update_app_tracker_settings_validation_error(self, mcp_server):
        with pytest.raises(Exception) as exc_info:
            await mcp_server.call_tool("tracker_settings_app_update", {"app_id": "app-1", "attributes": "not-a-dict"})
        assert "validation" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_tracker_settings_app_get_not_found(self, mcp_server):
        with patch("piwik_pro_mcp.tools.tracker_settings.tools.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance

            def _raise(*args, **kwargs):
                raise NotFoundError(status_code=404, message="not found", response_data={})

            mock_instance.tracker_settings.get_app_settings.side_effect = _raise

            with pytest.raises(Exception) as exc_info:
                await mcp_server.call_tool("tracker_settings_app_get", {"app_id": "app-1"})
            assert "not found" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_tracker_settings_app_update_empty_dict(self, mcp_server):
        with pytest.raises(Exception) as exc_info:
            await mcp_server.call_tool("tracker_settings_app_update", {"app_id": "app-1", "attributes": {}})
        assert "no update parameters provided" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_tracker_settings_global_update_empty_dict(self, mcp_server):
        with pytest.raises(Exception) as exc_info:
            await mcp_server.call_tool("tracker_settings_global_update", {"attributes": {}})
        assert "no update parameters provided" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_tracker_settings_global_update_validation_error(self, mcp_server):
        with pytest.raises(Exception) as exc_info:
            await mcp_server.call_tool("tracker_settings_global_update", {"attributes": "not-a-dict"})
        assert "validation" in str(exc_info.value).lower()
