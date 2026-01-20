"""Integration tests for MCP server functionality."""

import pytest


class TestMCPToolExistence:
    """Test existence of all MCP tools using parameterized tests."""

    # Expected tools list - used for both parametrized test and count verification
    EXPECTED_TOOLS = [
        # App Management Tools
        "apps_list",
        "apps_get",
        "tools_parameters_get",
        "apps_create",
        "apps_update",
        "apps_delete",
        # CDP Tools
        "activations_attributes_list",
        "audiences_list",
        "audiences_get",
        "audiences_create",
        "audiences_update",
        "audiences_delete",
        # Tag Manager Tools
        "tags_list",
        "tags_get",
        "templates_list",
        "templates_get_tag",
        "tags_list_triggers",
        "tags_copy",
        "tags_create",
        "tags_update",
        "tags_delete",
        "triggers_list",
        "triggers_get",
        "templates_list_triggers",
        "templates_get_trigger",
        "triggers_list_tags",
        "triggers_copy",
        "triggers_create",
        "variables_list",
        "variables_get",
        "templates_list_variables",
        "variables_copy",
        # Container Settings Tools
        "container_settings_get_installation_code",
        "container_settings_list",
        "templates_get_variable",
        "variables_create",
        "variables_update",
        "versions_list",
        "versions_get_draft",
        "versions_get_published",
        "versions_publish_draft",
        # Tracker Settings Tools
        "tracker_settings_global_get",
        "tracker_settings_global_update",
        "tracker_settings_app_get",
        "tracker_settings_app_update",
        "tracker_settings_app_delete",
        # Analytics Annotations Tools
        "analytics_annotations_create",
        "analytics_annotations_list",
        "analytics_annotations_get",
        "analytics_annotations_update",
        "analytics_annotations_delete",
        # Analytics Goals Tools
        "analytics_goals_create",
        "analytics_goals_list",
        "analytics_goals_get",
        "analytics_goals_update",
        "analytics_goals_delete",
        # Analytics Query Tools
        "analytics_query_execute",
        "analytics_dimensions_list",
        "analytics_metrics_list",
        "analytics_dimensions_details_list",
        "analytics_metrics_details_list",
        # Analytics Custom Dimensions Tools
        "analytics_custom_dimensions_create",
        "analytics_custom_dimensions_get",
        "analytics_custom_dimensions_get_slots",
        "analytics_custom_dimensions_list",
        "analytics_custom_dimensions_update",
    ]

    @pytest.fixture(scope="class")
    async def tool_names(self, mcp_server):
        """Fetch all tool names from the MCP server once for the entire test class."""
        tools = await mcp_server.list_tools()
        return [tool.name for tool in tools]

    def test_tool_count_matches_expected(self, tool_names):
        """Test that the total number of tools matches our expected list."""
        assert len(tool_names) == len(self.EXPECTED_TOOLS), (
            f"Expected {len(self.EXPECTED_TOOLS)} tools, but found {len(tool_names)}. "
            f"Expected: {sorted(self.EXPECTED_TOOLS)}, "
            f"Actual: {sorted(tool_names)}"
        )

    @pytest.mark.parametrize("expected_tool_name", EXPECTED_TOOLS)
    def test_tool_exists(self, tool_names, expected_tool_name):
        """Test that the specified tool exists in the MCP server."""
        assert expected_tool_name in tool_names, (
            f"Tool '{expected_tool_name}' not found in server. Available tools: {tool_names}"
        )


class TestSchemaResolvable:
    @pytest.mark.asyncio
    async def test_tool_schemas_resolvable_for_all_registered_tools(self, mcp_server):
        tools = await mcp_server.list_tools()
        tool_names = [t.name for t in tools]

        # Only check tools that our parameter discovery supports
        schema_tools = [
            "apps_create",
            "apps_update",
            "audiences_create",
            "audiences_update",
            "tags_create",
            "tags_update",
            "triggers_create",
            "variables_create",
            "variables_update",
        ]

        for name in schema_tools:
            assert name in tool_names
            result = await mcp_server.call_tool("tools_parameters_get", {"tool_name": name})
            assert isinstance(result, list) and len(result) == 1 and hasattr(result[0], "text")
