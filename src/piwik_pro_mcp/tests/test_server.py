"""Tests for MCP server creation and core functionality."""

import os
from unittest.mock import patch

import pytest
from mcp.server.fastmcp import FastMCP

from piwik_pro_mcp.server import create_mcp_server


class TestServerCreation:
    """Test MCP server creation and initialization."""

    def test_server_creation(self, mcp_server):
        """Test that the MCP server can be created successfully."""
        assert isinstance(mcp_server, FastMCP)
        assert mcp_server.name == "Piwik PRO Analytics Server 📊"


class TestServerEnvValidation:
    @pytest.mark.asyncio
    async def test_server_creation_missing_env_vars_produces_clear_error(self):
        # Unset env and ensure clear errors occur upon client creation attempts
        with patch.dict(
            os.environ,
            {
                "PIWIK_PRO_HOST": "",
                "PIWIK_PRO_CLIENT_ID": "",
                "PIWIK_PRO_CLIENT_SECRET": "",
            },
        ):
            mcp = create_mcp_server()
            # Calling any tool that needs client should raise
            with pytest.raises(Exception) as exc_info:
                await mcp.call_tool("apps_list", {"limit": 1, "offset": 0})

            message = str(exc_info.value).lower()
            assert "environment" in message or "client" in message or "host" in message

    @pytest.mark.asyncio
    async def test_env_missing_credentials_message(self):
        with patch.dict(
            os.environ,
            {
                "PIWIK_PRO_HOST": "example",
                "PIWIK_PRO_CLIENT_ID": "",
                "PIWIK_PRO_CLIENT_SECRET": "",
            },
        ):
            mcp = create_mcp_server()
            with pytest.raises(Exception) as exc_info:
                await mcp.call_tool("apps_list", {"limit": 1, "offset": 0})
            message = str(exc_info.value).lower()
            assert "client" in message or "credentials" in message
