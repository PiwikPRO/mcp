"""Tests for MCP server creation and core functionality."""

import os
import sys
from unittest.mock import patch

import pytest
from mcp.server.fastmcp import FastMCP

from piwik_pro_mcp import server as server_module
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


class TestServerCli:
    """Validate CLI argument handling for the server entrypoint."""

    def setup_method(self, _method):
        # Ensure argv is restored after each test
        self._orig_argv = sys.argv[:]

    def teardown_method(self, _method):
        sys.argv = self._orig_argv

    def test_main_defaults_to_stdio_transport(self, mock_server_for_cli):
        sys.argv = ["server.py"]
        server_module.main()
        assert mock_server_for_cli["captured_kwargs"] == {"transport": "stdio"}

    def test_main_http_transport_with_overrides(self, mock_server_for_cli):
        sys.argv = [
            "server.py",
            "--transport",
            "streamable-http",
            "--host",
            "127.0.0.1",
            "--port",
            "9000",
            "--path",
            "/custom",
        ]

        server_module.main()

        assert mock_server_for_cli["captured_kwargs"] == {"transport": "streamable-http"}
        server = mock_server_for_cli["get_server"]()
        assert server.settings.host == "127.0.0.1"
        assert server.settings.port == 9000
        assert server.settings.streamable_http_path == "/custom"

    def test_main_http_transport_defaults_when_not_provided(self, mock_server_for_cli):
        sys.argv = ["server.py", "--transport", "streamable-http"]

        server_module.main()

        assert mock_server_for_cli["captured_kwargs"] == {"transport": "streamable-http"}
        server = mock_server_for_cli["get_server"]()
        assert server.settings.host == server_module.DEFAULT_HTTP_HOST
        assert server.settings.port == server_module.DEFAULT_HTTP_PORT
        assert server.settings.streamable_http_path == server_module.DEFAULT_HTTP_PATH

    def test_main_rejects_http_arguments_for_stdio(self, monkeypatch):
        monkeypatch.setattr(server_module, "validate_environment", lambda: None)
        sys.argv = ["server.py", "--host", "127.0.0.1"]

        with pytest.raises(SystemExit):
            server_module.main()
