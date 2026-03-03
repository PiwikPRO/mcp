"""Integration tests for MCP server functionality."""

import os
from unittest.mock import patch

import pytest

from ..common.settings import safe_mode_enabled
from ..server import create_mcp_server

# Single source of truth for tool classification.
# When adding a new tool, place it in the appropriate list below.

READ_ONLY_TOOLS = [
    # Parameter Discovery
    "tools_parameters_get",
    # App Management
    "apps_list",
    "apps_get",
    # CDP
    "activations_attributes_list",
    "audiences_list",
    "audiences_get",
    # Tag Manager
    "tags_list",
    "tags_get",
    "tags_list_triggers",
    "triggers_list",
    "triggers_get",
    "triggers_list_tags",
    "variables_list",
    "variables_get",
    "templates_list",
    "templates_get_tag",
    "templates_list_triggers",
    "templates_get_trigger",
    "templates_list_variables",
    "templates_get_variable",
    "versions_list",
    "versions_get_draft",
    "versions_get_published",
    # Container Settings
    "container_settings_get_installation_code",
    "container_settings_list",
    # Tracker Settings
    "tracker_settings_global_get",
    "tracker_settings_app_get",
    # Analytics
    "analytics_annotations_list",
    "analytics_annotations_get",
    "analytics_goals_list",
    "analytics_goals_get",
    "analytics_query_execute",
    "analytics_dimensions_list",
    "analytics_metrics_list",
    "analytics_dimensions_details_list",
    "analytics_metrics_details_list",
    "analytics_custom_dimensions_list",
    "analytics_custom_dimensions_get",
    "analytics_custom_dimensions_get_slots",
]

WRITE_TOOLS = [
    # App Management
    "apps_create",
    "apps_update",
    "apps_delete",
    # CDP
    "audiences_create",
    "audiences_update",
    "audiences_delete",
    # Tag Manager
    "tags_copy",
    "tags_create",
    "tags_update",
    "tags_delete",
    "triggers_copy",
    "triggers_create",
    "variables_copy",
    "variables_create",
    "variables_update",
    "versions_publish_draft",
    # Tracker Settings
    "tracker_settings_global_update",
    "tracker_settings_app_update",
    "tracker_settings_app_delete",
    # Analytics
    "analytics_annotations_create",
    "analytics_annotations_update",
    "analytics_annotations_delete",
    "analytics_goals_create",
    "analytics_goals_update",
    "analytics_goals_delete",
    "analytics_custom_dimensions_create",
    "analytics_custom_dimensions_update",
]

ALL_TOOLS = READ_ONLY_TOOLS + WRITE_TOOLS


class TestMCPToolExistence:
    """Test existence of all MCP tools using parameterized tests."""

    @pytest.fixture(scope="class")
    async def tool_names(self, mcp_server):
        """Fetch all tool names from the MCP server once for the entire test class."""
        tools = await mcp_server.list_tools()
        return [tool.name for tool in tools]

    def test_tool_count_matches_expected(self, tool_names):
        """Test that the total number of tools matches our expected list."""
        assert len(tool_names) == len(ALL_TOOLS), (
            f"Expected {len(ALL_TOOLS)} tools, but found {len(tool_names)}. "
            f"Expected: {sorted(ALL_TOOLS)}, "
            f"Actual: {sorted(tool_names)}"
        )

    @pytest.mark.parametrize("expected_tool_name", ALL_TOOLS)
    def test_tool_exists(self, tool_names, expected_tool_name):
        """Test that the specified tool exists in the MCP server."""
        assert expected_tool_name in tool_names, (
            f"Tool '{expected_tool_name}' not found in server. Available tools: {tool_names}"
        )


class TestSafeModeToolFiltering:
    """Test that safe mode correctly filters out write tools and keeps only read-only tools."""

    @pytest.fixture(scope="class")
    async def tool_names(self):
        """Create a safe mode server and fetch tool names."""
        safe_mode_enabled.cache_clear()

        with patch.dict(
            os.environ,
            {
                "PIWIK_PRO_HOST": "test-instance.piwik.pro",
                "PIWIK_PRO_CLIENT_ID": "test-client-id",
                "PIWIK_PRO_CLIENT_SECRET": "test-client-secret",
                "PIWIK_PRO_SAFE_MODE": "1",
            },
        ):
            server = create_mcp_server()
            tools = await server.list_tools()

        safe_mode_enabled.cache_clear()
        return [tool.name for tool in tools]

    def test_read_only_tool_count_matches_expected(self, tool_names):
        """Test that the total number of tools in safe mode matches expected read-only list."""
        assert len(tool_names) == len(READ_ONLY_TOOLS), (
            f"Expected {len(READ_ONLY_TOOLS)} read-only tools, but found {len(tool_names)}. "
            f"Expected: {sorted(READ_ONLY_TOOLS)}, "
            f"Actual: {sorted(tool_names)}"
        )

    @pytest.mark.parametrize("expected_tool_name", READ_ONLY_TOOLS)
    def test_read_only_tool_is_available(self, tool_names, expected_tool_name):
        """Test that read-only tool remains available in safe mode."""
        assert expected_tool_name in tool_names, (
            f"Read-only tool '{expected_tool_name}' not found in safe mode server. Available tools: {tool_names}"
        )

    @pytest.mark.parametrize("write_tool_name", WRITE_TOOLS)
    def test_write_tool_is_removed(self, tool_names, write_tool_name):
        """Test that write tool is removed in safe mode."""
        assert write_tool_name not in tool_names, (
            f"Write tool '{write_tool_name}' should not be available in safe mode."
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
