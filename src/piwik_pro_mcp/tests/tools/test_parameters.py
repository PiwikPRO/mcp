"""Tests for parameter discovery and validation functionality."""

import json

import pytest
from mcp.server.fastmcp.exceptions import ToolError

from piwik_pro_mcp.common.tool_schemas import get_all_registered_tools, get_tool_schema


class TestParameterDiscoveryFunctional:
    """Functional tests for parameter discovery through MCP server."""

    @pytest.mark.asyncio
    async def test_tools_parameters_get_update_app_functional(self, mcp_server):
        """Test that tools_parameters_get returns correct schema for apps_update through MCP."""
        # Call the tool through MCP server
        tools = await mcp_server.list_tools()
        tool_names = [tool.name for tool in tools]

        # Verify the tool exists
        assert "tools_parameters_get" in tool_names

        # Call the tool functionally
        result = await mcp_server.call_tool("tools_parameters_get", {"tool_name": "apps_update"})

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

        # Check for specific expected fields from AppEditableAttributes
        properties = schema_dict["properties"]
        assert "name" in properties
        assert "urls" in properties
        assert "timezone" in properties
        assert "currency" in properties
        assert "gdpr" in properties

        # Verify field types (note: optional fields use anyOf structure)
        # For optional fields, check the first type in anyOf
        assert properties["name"]["anyOf"][0]["type"] == "string"
        assert properties["urls"]["anyOf"][0]["type"] == "array"
        assert properties["timezone"]["anyOf"][0]["type"] == "string"
        assert properties["currency"]["anyOf"][0]["type"] == "string"
        assert properties["gdpr"]["anyOf"][0]["type"] == "boolean"

        # Verify field descriptions exist
        assert "description" in properties["name"]
        assert "description" in properties["urls"]

    @pytest.mark.asyncio
    async def test_tools_parameters_get_apps_update_complete_schema_functional(self, mcp_server):
        """Test that tools_parameters_get returns complete schema for apps_update through MCP."""
        result = await mcp_server.call_tool("tools_parameters_get", {"tool_name": "apps_update"})

        assert isinstance(result, list)
        assert len(result) == 1
        assert hasattr(result[0], "text")

        schema = json.loads(result[0].text)

        assert isinstance(schema, dict)
        assert schema["type"] == "object"
        assert schema["title"] == "AppEditableAttributes"
        assert "description" in schema
        assert schema["description"] == "Editable attributes of an app."

        # Verify properties exist
        assert "properties" in schema
        properties = schema["properties"]

        # Check for all expected fields from AppEditableAttributes
        expected_fields = [
            "name",
            "urls",
            "timezone",
            "currency",
            "eCommerceTracking",
            "delay",
            "gdpr",
            "gdprUserModeEnabled",
            "privacyCookieDomainsEnabled",
            "privacyCookieExpirationPeriod",
            "privacyCookieDomains",
            "gdprDataAnonymization",
            "sharepointIntegration",
            "gdprDataAnonymizationMode",
            "privacyUseCookies",
            "privacyUseFingerprinting",
            "cnil",
            "sessionIdStrictPrivacyMode",
            "realTimeDashboards",
        ]

        for field in expected_fields:
            assert field in properties, f"Field '{field}' missing from schema"

        # Verify specific field structures for key fields
        # Test name field
        name_field = properties["name"]
        assert "anyOf" in name_field
        assert name_field["anyOf"][0]["type"] == "string"
        assert name_field["anyOf"][0]["maxLength"] == 90
        assert name_field["anyOf"][1]["type"] == "null"
        assert name_field["description"] == "App name"

        # Test urls field (array type)
        urls_field = properties["urls"]
        assert "anyOf" in urls_field
        assert urls_field["anyOf"][0]["type"] == "array"
        assert urls_field["anyOf"][0]["items"]["type"] == "string"
        assert urls_field["anyOf"][1]["type"] == "null"
        assert urls_field["description"] == "List of URLs under which the app is available"

        # Verify $defs section for enums
        assert "$defs" in schema
        assert "GdprDataAnonymizationMode" in schema["$defs"]
        enum_def = schema["$defs"]["GdprDataAnonymizationMode"]
        assert enum_def["type"] == "string"
        assert "enum" in enum_def
        assert "no_device_storage" in enum_def["enum"]
        assert "session_cookie_id" in enum_def["enum"]
        assert enum_def["description"] == "GDPR data anonymization mode."

        # Verify all fields have default null (since they're optional)
        for field_name, field_schema in properties.items():
            assert field_schema["default"] is None, f"Field '{field_name}' should have default null"

    @pytest.mark.asyncio
    async def test_tools_parameters_get_unknown_tool_functional(self, mcp_server):
        """Test that tools_parameters_get raises error for unknown tools through MCP."""
        with pytest.raises(ToolError) as exc_info:
            await mcp_server.call_tool("tools_parameters_get", {"tool_name": "nonexistent_tool"})

        # Verify error message
        assert "Unknown tool" in str(exc_info.value)


class TestParameterRegistryConsistency:
    @pytest.mark.asyncio
    async def test_all_mcp_tools_have_parameter_models_unless_exempt(self, mcp_server):
        """
        Ensure every MCP tool is represented in TOOL_PARAMETER_MODELS unless explicitly exempt.

        Why this matters:
        - Tools that accept JSON-attributes (create/update/list-with-filters) should expose schemas via
          tools_parameters_get so UIs/agents can discover parameters at runtime.
        - This test is intentionally "future-hostile": adding a new eligible tool will FAIL until
          it's registered in TOOL_PARAMETER_MODELS (or added to the exemptions below if it shouldn't have a schema).

        When to register a tool here:
        - If a tool takes an "attributes" dict (create/update) or a "filters" dict (list) → register a model.
        - If a tool only takes simple scalars/identifiers (get/delete/copy, read-only fetches, template discovery),
          add it to the exemptions list below.
        """

        registry = set(get_all_registered_tools())
        tools = await mcp_server.list_tools()
        all_tool_names = sorted(t.name for t in tools)

        exemptions = {
            # Discovery/meta
            "tools_parameters_get",
            # Apps read-only / delete
            "apps_list",
            "apps_get",
            "apps_delete",
            # CDP read-only / delete
            "audiences_list",
            "audiences_get",
            "audiences_delete",
            "activations_attributes_list",
            # Tag Manager (read-only / relationships / delete / copy)
            "tags_list",
            "tags_get",
            "tags_list_triggers",
            "triggers_list_tags",
            "tags_delete",
            "tags_copy",
            "triggers_list",
            "triggers_get",
            "triggers_copy",
            "variables_list",
            "variables_get",
            "variables_copy",
            # Tag Manager versions
            "versions_list",
            "versions_get_draft",
            "versions_get_published",
            "versions_publish_draft",
            # Templates discovery
            "templates_list",
            "templates_get_tag",
            "templates_list_triggers",
            "templates_get_trigger",
            "templates_list_variables",
            "templates_get_variable",
            # Container settings (read-only)
            "container_settings_get_installation_code",
            "container_settings_list",
            # Tracker settings (read-only / delete)
            "tracker_settings_global_get",
            "tracker_settings_app_get",
            "tracker_settings_app_delete",
            # Analytics annotations (annotations)
            "analytics_annotations_create",
            "analytics_annotations_list",
            "analytics_annotations_get",
            "analytics_annotations_delete",
            "analytics_annotations_update",
            # Analytics goals (read-only / delete)
            "analytics_goals_list",
            "analytics_goals_get",
            "analytics_goals_delete",
            "analytics_goals_create",
            "analytics_goals_update",
            # Analytics query
            "analytics_dimensions_list",
            "analytics_metrics_list",
            "analytics_dimensions_details_list",
            "analytics_metrics_details_list",
            # Analytics custom dimensions (read-only / delete)
            "analytics_custom_dimensions_create",
            "analytics_custom_dimensions_get",
            "analytics_custom_dimensions_get_slots",
            "analytics_custom_dimensions_list",
            "analytics_custom_dimensions_update",
        }

        missing_models = [name for name in all_tool_names if name not in exemptions and name not in registry]
        assert not missing_models, (
            "These tools are missing parameter models in TOOL_PARAMETER_MODELS and must be added: "
            f"{missing_models}. Registered models: {sorted(registry)}"
        )

    def test_parameter_schema_titles_and_types_parametrized_across_tools(self):
        # Spot-check schema shape basics across registry
        tools = get_all_registered_tools()
        for tool in tools:
            schema = get_tool_schema(tool)
            assert isinstance(schema, dict)
            assert schema.get("type") == "object"
            assert "properties" in schema

    @pytest.mark.asyncio
    async def test_tools_parameters_get_empty_tool_name_functional(self, mcp_server):
        """Test error handling for empty tool name through MCP."""
        with pytest.raises(ToolError) as exc_info:
            await mcp_server.call_tool("tools_parameters_get", {"tool_name": ""})

        # Verify error message
        assert "Unknown tool" in str(exc_info.value)
