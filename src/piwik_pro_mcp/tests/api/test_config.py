"""Tests for API configuration."""

import logging
import os
from unittest.mock import patch

import pytest

from piwik_pro_mcp.api.config import Config
from piwik_pro_mcp.common.settings import allow_insecure_host


class TestConfigHostValidation:
    """Tests for PIWIK_PRO_HOST scheme handling."""

    def setup_method(self):
        allow_insecure_host.cache_clear()

    def teardown_method(self):
        allow_insecure_host.cache_clear()

    def test_scheme_less_host_is_upgraded_to_https(self):
        config = Config(host="example.piwik.pro", client_id="id", client_secret="secret")

        assert config.host == "https://example.piwik.pro"
        assert config.base_url == "https://example.piwik.pro"

    def test_https_host_is_preserved(self):
        config = Config(host="https://example.piwik.pro", client_id="id", client_secret="secret")

        assert config.host == "https://example.piwik.pro"

    def test_explicit_http_host_is_rejected_by_default(self):
        with pytest.raises(ValueError, match="Insecure HTTP host is not allowed"):
            Config(host="http://example.piwik.pro", client_id="id", client_secret="secret")

    def test_explicit_http_host_allowed_with_opt_in_flag(self, caplog):
        with patch.dict(os.environ, {"PIWIK_PRO_ALLOW_INSECURE_HOST": "1"}):
            allow_insecure_host.cache_clear()

            with caplog.at_level(logging.WARNING):
                config = Config(host="http://example.piwik.pro", client_id="id", client_secret="secret")

            assert config.host == "http://example.piwik.pro"
            assert any("unencrypted connection" in record.message for record in caplog.records)

    def test_missing_host_raises(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("PIWIK_PRO_HOST", None)
            with pytest.raises(ValueError, match="Host is required"):
                Config(host=None, client_id="id", client_secret="secret")
