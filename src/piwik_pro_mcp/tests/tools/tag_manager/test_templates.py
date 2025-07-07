"""Tests for Tag Manager template discovery functionality."""

import json

import pytest


class TestTemplateDiscoveryFunctional:
    """Functional tests for template discovery through MCP."""

    @pytest.mark.asyncio
    async def test_list_available_parameters_tag_manager_create_tools_functional(self, mcp_server):
        """Test that list_available_parameters returns correct schema for Tag Manager create tools."""
        # Test create_tag
        result = await mcp_server.call_tool("tools_parameters_get", {"tool_name": "tags_create"})

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
        assert schema_dict["title"] == "TagManagerCreateAttributes"

        # Check for expected fields
        properties = schema_dict["properties"]
        assert "name" in properties
        assert "template" in properties
        assert "is_active" in properties

        # Verify field types
        assert properties["name"]["type"] == "string"
        assert properties["template"]["type"] == "string"
        assert properties["is_active"]["anyOf"][0]["type"] == "boolean"

        # Test create_trigger
        result = await mcp_server.call_tool("tools_parameters_get", {"tool_name": "triggers_create"})

        schema = result[0].text
        schema_dict = json.loads(schema)
        assert schema_dict["title"] == "TriggerAttributes"

        # Test create_variable
        result = await mcp_server.call_tool("tools_parameters_get", {"tool_name": "variables_create"})

        schema = result[0].text
        schema_dict = json.loads(schema)
        assert schema_dict["title"] == "VariableCreateAttributes"

    @pytest.mark.asyncio
    async def test_trigger_template_discovery_tools(self, mcp_server):
        result = await mcp_server.call_tool("templates_list_triggers", {})
        # Tools may return list-of-content (JSON string). Handle that case.
        if isinstance(result, list):
            data = json.loads(result[0].text)
        else:
            _, data = result
        assert "available_templates" in data and isinstance(data["available_templates"], list)

        # Probe one template (if any available in assets)
        if data["available_templates"]:
            template = data["available_templates"][0]
            result = await mcp_server.call_tool("templates_get_trigger", {"template_name": template})
            if isinstance(result, list):
                tdata = json.loads(result[0].text)
            else:
                _, tdata = result
            assert isinstance(tdata, dict) and tdata

    @pytest.mark.asyncio
    async def test_variable_template_discovery_tools(self, mcp_server):
        result = await mcp_server.call_tool("templates_list_variables", {})
        if isinstance(result, list):
            data = json.loads(result[0].text)
        else:
            _, data = result
        assert "available_templates" in data and isinstance(data["available_templates"], list)

        if data["available_templates"]:
            template = data["available_templates"][0]
            result = await mcp_server.call_tool("templates_get_variable", {"template_name": template})
            if isinstance(result, list):
                tdata = json.loads(result[0].text)
            else:
                _, tdata = result
            assert isinstance(tdata, dict) and tdata

    @pytest.mark.asyncio
    async def test_unknown_templates_list_suggestions(self, mcp_server):
        # unknown template names should produce error listing available ones
        with pytest.raises(Exception) as exc_info:
            await mcp_server.call_tool("templates_get_tag", {"template_name": "__unknown__"})
        assert "available" in str(exc_info.value).lower() or "template" in str(exc_info.value).lower()

        with pytest.raises(Exception) as exc_info2:
            await mcp_server.call_tool("templates_get_trigger", {"template_name": "__unknown__"})
        assert "available" in str(exc_info2.value).lower() or "trigger" in str(exc_info2.value).lower()

        with pytest.raises(Exception) as exc_info3:
            await mcp_server.call_tool("templates_get_variable", {"template_name": "__unknown__"})
        assert "available" in str(exc_info3.value).lower() or "variable" in str(exc_info3.value).lower()
