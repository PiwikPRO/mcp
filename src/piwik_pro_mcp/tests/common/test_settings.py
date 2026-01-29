"""Tests for settings module."""

import os
from unittest.mock import patch

from piwik_pro_mcp.common.settings import (
    _DEFAULT_HTTP_ALLOWED_HOSTS,
    http_allowed_hosts,
)


class TestHttpAllowedHosts:
    """Tests for http_allowed_hosts function."""

    def setup_method(self):
        """Clear the LRU cache before each test."""
        http_allowed_hosts.cache_clear()

    def teardown_method(self):
        """Clear the LRU cache after each test."""
        http_allowed_hosts.cache_clear()

    def test_returns_defaults_when_env_not_set(self):
        """When PIWIK_PRO_HTTP_ALLOWED_HOSTS is not set, return default localhost variants."""
        with patch.dict(os.environ, {}, clear=False):
            # Ensure the env var is not set
            os.environ.pop("PIWIK_PRO_HTTP_ALLOWED_HOSTS", None)
            http_allowed_hosts.cache_clear()

            result = http_allowed_hosts()

            assert result == _DEFAULT_HTTP_ALLOWED_HOSTS
            assert "localhost:*" in result
            assert "127.0.0.1:*" in result
            assert "::1:*" in result
            assert "[::1]:*" in result

    def test_includes_defaults_with_custom_hosts(self):
        """When PIWIK_PRO_HTTP_ALLOWED_HOSTS is set, include both defaults and custom hosts."""
        with patch.dict(
            os.environ,
            {"PIWIK_PRO_HTTP_ALLOWED_HOSTS": "mcp.example.com:*,internal.local:8080"},
        ):
            http_allowed_hosts.cache_clear()

            result = http_allowed_hosts()

            # Defaults should be present
            assert "localhost:*" in result
            assert "127.0.0.1:*" in result
            assert "::1:*" in result
            assert "[::1]:*" in result

            # Custom hosts should be present
            assert "mcp.example.com:*" in result
            assert "internal.local:8080" in result

    def test_custom_hosts_appended_after_defaults(self):
        """Custom hosts should be appended after the default localhost variants."""
        with patch.dict(
            os.environ,
            {"PIWIK_PRO_HTTP_ALLOWED_HOSTS": "custom.host:9000"},
        ):
            http_allowed_hosts.cache_clear()

            result = http_allowed_hosts()

            # Defaults come first
            assert result[: len(_DEFAULT_HTTP_ALLOWED_HOSTS)] == _DEFAULT_HTTP_ALLOWED_HOSTS
            # Custom host comes after
            assert result[-1] == "custom.host:9000"

    def test_handles_whitespace_in_custom_hosts(self):
        """Whitespace around custom hosts should be stripped."""
        with patch.dict(
            os.environ,
            {"PIWIK_PRO_HTTP_ALLOWED_HOSTS": "  host1.com:*  ,  host2.com:8080  "},
        ):
            http_allowed_hosts.cache_clear()

            result = http_allowed_hosts()

            assert "host1.com:*" in result
            assert "host2.com:8080" in result
            # No whitespace-padded entries
            assert "  host1.com:*  " not in result
            assert "  host2.com:8080  " not in result

    def test_handles_empty_entries_in_custom_hosts(self):
        """Empty entries in the comma-separated list should be ignored."""
        with patch.dict(
            os.environ,
            {"PIWIK_PRO_HTTP_ALLOWED_HOSTS": "host1.com:*,,host2.com:*,"},
        ):
            http_allowed_hosts.cache_clear()

            result = http_allowed_hosts()

            custom_hosts = result[len(_DEFAULT_HTTP_ALLOWED_HOSTS) :]
            assert custom_hosts == ["host1.com:*", "host2.com:*"]

    def test_single_custom_host(self):
        """A single custom host without commas should work."""
        with patch.dict(
            os.environ,
            {"PIWIK_PRO_HTTP_ALLOWED_HOSTS": "single.host.com:*"},
        ):
            http_allowed_hosts.cache_clear()

            result = http_allowed_hosts()

            assert len(result) == len(_DEFAULT_HTTP_ALLOWED_HOSTS) + 1
            assert result[-1] == "single.host.com:*"

    def test_empty_env_value_returns_defaults_only(self):
        """An empty env value should return only defaults."""
        with patch.dict(
            os.environ,
            {"PIWIK_PRO_HTTP_ALLOWED_HOSTS": ""},
        ):
            http_allowed_hosts.cache_clear()

            result = http_allowed_hosts()

            assert result == _DEFAULT_HTTP_ALLOWED_HOSTS

    def test_whitespace_only_env_value_returns_defaults_only(self):
        """A whitespace-only env value should return only defaults."""
        with patch.dict(
            os.environ,
            {"PIWIK_PRO_HTTP_ALLOWED_HOSTS": "   "},
        ):
            http_allowed_hosts.cache_clear()

            result = http_allowed_hosts()

            assert result == _DEFAULT_HTTP_ALLOWED_HOSTS

    def test_returns_copy_not_reference(self):
        """The function should return a copy, not a reference to the internal list."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("PIWIK_PRO_HTTP_ALLOWED_HOSTS", None)
            http_allowed_hosts.cache_clear()

            result = http_allowed_hosts()

            # Modify result and ensure the original _DEFAULT_HTTP_ALLOWED_HOSTS is unchanged
            result.append("modified")
            assert "modified" not in _DEFAULT_HTTP_ALLOWED_HOSTS
