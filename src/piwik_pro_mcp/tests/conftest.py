"""Pytest configuration and fixtures for MCP server tests."""

import os
from unittest.mock import patch

import pytest

from .. import server as server_module
from ..common.settings import safe_mode_enabled
from ..server import create_mcp_server


@pytest.fixture(scope="class")
def mock_env_vars():
    """Mock environment variables needed for server initialization."""
    # Clear LRU cache to ensure fresh environment variable reads
    safe_mode_enabled.cache_clear()

    with patch.dict(
        os.environ,
        {
            "PIWIK_PRO_HOST": "test-instance.piwik.pro",
            "PIWIK_PRO_CLIENT_ID": "test-client-id",
            "PIWIK_PRO_CLIENT_SECRET": "test-client-secret",
            "PIWIK_PRO_SAFE_MODE": "0",  # Disable safe mode for tests
        },
    ):
        yield

    # Clear cache after tests to avoid affecting other test modules
    safe_mode_enabled.cache_clear()


@pytest.fixture(scope="class")
def mcp_server(mock_env_vars):
    """Create a configured MCP server instance for testing."""
    return create_mcp_server()


@pytest.fixture
def mock_server_for_cli(monkeypatch):
    """Fixture that mocks server creation for CLI tests.

    Returns a dict with:
    - captured_kwargs: dict populated with kwargs passed to server.run()
    - get_server: function to access the created server instance
    """
    captured_kwargs = {}
    created_server = None

    def fake_run(**kwargs):
        captured_kwargs.update(kwargs)

    def fake_create_server():
        nonlocal created_server
        created_server = create_mcp_server()
        monkeypatch.setattr(created_server, "run", fake_run)
        return created_server

    def get_server():
        return created_server

    monkeypatch.setattr(server_module, "validate_environment", lambda: None)
    monkeypatch.setattr(server_module, "create_mcp_server", fake_create_server)

    return {"captured_kwargs": captured_kwargs, "get_server": get_server}
