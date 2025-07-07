"""Pytest configuration and fixtures for MCP server tests."""

import os
from unittest.mock import patch

import pytest

from ..server import create_mcp_server


@pytest.fixture(scope="class")
def mock_env_vars():
    """Mock environment variables needed for server initialization."""
    with patch.dict(
        os.environ,
        {
            "PIWIK_PRO_HOST": "test-instance.piwik.pro",
            "PIWIK_PRO_CLIENT_ID": "test-client-id",
            "PIWIK_PRO_CLIENT_SECRET": "test-client-secret",
        },
    ):
        yield


@pytest.fixture(scope="class")
def mcp_server(mock_env_vars):
    """Create a configured MCP server instance for testing."""
    return create_mcp_server()
