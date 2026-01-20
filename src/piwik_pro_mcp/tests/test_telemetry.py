"""Unit tests for telemetry utilities and server telemetry toggling."""

import asyncio
import os
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, patch
from urllib.parse import parse_qs

import httpx
import pytest
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from piwik_pro_mcp.common.settings import telemetry_enabled
from piwik_pro_mcp.common.telemetry import (
    TelemetryEvent,
    TelemetrySender,
    TelemetryStatus,
    mcp_telemetry_wrapper,
)
from piwik_pro_mcp.server import create_mcp_server


def test_server_respects_env_and_disables_telemetry_when_flag_is_zero():
    with patch.dict(os.environ, {"PIWIK_PRO_TELEMETRY": "0"}, clear=False):
        telemetry_enabled.cache_clear()
        with patch("piwik_pro_mcp.server.mcp_telemetry_wrapper", new=MagicMock()) as mock_wrapper:
            _ = create_mcp_server()
            mock_wrapper.assert_not_called()
    telemetry_enabled.cache_clear()


def test_server_instruments_telemetry_when_env_flag_is_one():
    with patch.dict(os.environ, {"PIWIK_PRO_TELEMETRY": "1"}, clear=False):
        telemetry_enabled.cache_clear()
        with patch("piwik_pro_mcp.server.mcp_telemetry_wrapper", new=MagicMock()) as mock_wrapper:
            _ = create_mcp_server()
            mock_wrapper.assert_called_once()
    telemetry_enabled.cache_clear()


class _FakeAsyncClient:
    """Minimal async httpx client stub capturing POST payloads."""

    def __init__(self, *, timeout: Optional[float] = None) -> None:
        self.timeout = timeout
        self.captured: Dict[str, Any] = {}

    async def __aenter__(self) -> "_FakeAsyncClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        return None

    async def post(self, url: str, *, json: Dict[str, Any], headers: Dict[str, str]) -> None:
        self.captured = {"url": url, "json": json, "headers": headers}


@pytest.mark.asyncio
async def test_telemetry_sender_encodes_expected_query(monkeypatch):
    # Arrange: replace httpx.AsyncClient with our stub
    def _factory(**kwargs):
        # Propagate timeout to the instance for potential assertions
        return _FakeAsyncClient(timeout=kwargs.get("timeout"))

    monkeypatch.setattr(httpx, "AsyncClient", _factory)

    sender = TelemetrySender(endpoint_url="https://success.piwik.pro/ppms.php", timeout_seconds=1.5, enabled=True)
    event = TelemetryEvent(
        tool_name="test_tool",
        status=TelemetryStatus.SUCCESS,
        duration_ms=123,
        error_message=None,
        client_name="unit-test-client",
        client_version="1.0.0",
        event_name="test_tool",
        visitor_id="0123456789abcdef",
    )

    # Act
    # We need access to the instance used inside send_event; build a small shim to capture
    captured: Dict[str, Any] = {}

    class _CaptureClient(_FakeAsyncClient):
        async def post(self, url: str, *, json: Dict[str, Any], headers: Dict[str, str]) -> None:  # type: ignore[override]
            nonlocal captured
            captured = {"url": url, "json": json, "headers": headers}

    def _capture_factory(**kwargs):
        return _CaptureClient(timeout=kwargs.get("timeout"))

    monkeypatch.setattr(httpx, "AsyncClient", _capture_factory)
    await sender.send_event(event)

    # Assert
    assert captured["url"] == "https://success.piwik.pro/ppms.php"
    assert captured["headers"]["Content-Type"] == "application/json"
    assert isinstance(captured["json"], dict)
    assert "requests" in captured["json"]
    reqs = captured["json"]["requests"]
    assert isinstance(reqs, list) and len(reqs) == 1
    query = reqs[0]
    assert query.startswith("?")

    parsed = parse_qs(query[1:])
    # Required keys present
    for key in [
        "dimension1",
        "dimension2",
        "dimension3",
        "rec",
        "idsite",
        "action_name",
        "e_c",
        "e_a",
        "e_n",
        "e_v",
        "_id",
    ]:
        assert key in parsed
    # Optional error message should be omitted when None
    assert "dimension4" not in parsed

    # Client name/version should be present when provided
    assert parsed["dimension5"] == ["unit-test-client"]
    assert parsed["dimension6"] == ["1.0.0"]

    assert parsed["dimension1"] == ["test_tool"]
    assert parsed["dimension2"] == ["success"]
    assert parsed["dimension3"] == ["123"]
    assert parsed["rec"] == ["1"]
    assert parsed["action_name"] == ["mcp_tool_call"]
    assert parsed["e_c"] == ["MCP"]
    assert parsed["e_a"] == ["mcp_tool_call"]
    assert parsed["e_n"] == ["test_tool"]
    assert parsed["e_v"] == ["1"]
    assert parsed["_id"] == ["0123456789abcdef"]
    # id_site defaults to a fixed UUID; just ensure it is non-empty
    assert parsed["idsite"][0]


@pytest.mark.asyncio
async def test_mcp_wrapper_populates_event_fields_for_tool_success(monkeypatch):
    # Capture outgoing request payload
    captured: Dict[str, Any] = {}

    class _CaptureClient(_FakeAsyncClient):
        async def post(self, url: str, *, json: Dict[str, Any], headers: Dict[str, str]) -> None:  # type: ignore[override]
            nonlocal captured
            captured = {"url": url, "json": json, "headers": headers}

    def _capture_factory(**kwargs):
        return _CaptureClient(timeout=kwargs.get("timeout"))

    monkeypatch.setattr(httpx, "AsyncClient", _capture_factory)

    # Create a minimal FastMCP and instrument telemetry
    mcp = FastMCP("test")
    sender = TelemetrySender(endpoint_url="https://success.piwik.pro/ppms.php")
    mcp_telemetry_wrapper(mcp, sender)

    # Register a simple tool
    @mcp.tool()
    def sample_tool(x: int) -> int:  # noqa: D401 - simple demo tool
        """Return the same integer."""
        return x

    # Call tool
    await mcp.call_tool("sample_tool", {"x": 1})
    # Allow background task to flush
    await asyncio.sleep(0.10)

    # Validate emitted telemetry fields from wrapper-specific defaults
    reqs = captured["json"]["requests"]
    query = reqs[0]
    parsed = parse_qs(query[1:])
    assert parsed["e_c"] == ["MCP"]
    assert parsed["e_a"] == ["sample_tool"]
    assert parsed["e_n"] == ["sample_tool"]
    # On success, wrapper sets event_value to 0
    assert parsed["e_v"] == ["0"]
    # Wrapper assigns a 16-char visitor id
    assert "_id" in parsed and len(parsed["_id"][0]) == 16
    # Wrapper should include client metadata when context is available
    assert parsed["dimension1"] == ["sample_tool"]
    assert parsed["dimension2"] == ["success"]
    assert parsed["dimension5"] == ["unknown"]
    assert parsed["dimension6"] == ["unknown"]


@pytest.mark.asyncio
async def test_mcp_wrapper_populates_event_fields_for_tool_error(monkeypatch):
    # Capture outgoing request payload
    captured: Dict[str, Any] = {}

    class _CaptureClient(_FakeAsyncClient):
        async def post(self, url: str, *, json: Dict[str, Any], headers: Dict[str, str]) -> None:  # type: ignore[override]
            nonlocal captured
            captured = {"url": url, "json": json, "headers": headers}

    def _capture_factory(**kwargs):
        return _CaptureClient(timeout=kwargs.get("timeout"))

    monkeypatch.setattr(httpx, "AsyncClient", _capture_factory)

    # Create a minimal FastMCP and instrument telemetry
    mcp = FastMCP("test")
    sender = TelemetrySender(endpoint_url="https://success.piwik.pro/ppms.php")
    mcp_telemetry_wrapper(mcp, sender)

    # Register a tool that fails
    @mcp.tool()
    def failing_tool(x: int) -> int:  # noqa: D401 - simple demo tool
        """Always raise to simulate an error."""
        raise RuntimeError("boom")

    # Call tool and expect an error to be raised
    with pytest.raises(ToolError):
        await mcp.call_tool("failing_tool", {"x": 1})

    # Allow background task to flush
    await asyncio.sleep(0.10)

    # Validate emitted telemetry fields for error case
    reqs = captured["json"]["requests"]
    query = reqs[0]
    parsed = parse_qs(query[1:])
    assert parsed["e_c"] == ["MCP"]
    assert parsed["e_a"] == ["failing_tool"]
    assert parsed["e_n"] == ["failing_tool"]
    # On error, wrapper sets event_value to 1
    assert parsed["e_v"] == ["1"]
    # Wrapper assigns a 16-char visitor id
    assert "_id" in parsed and len(parsed["_id"][0]) == 16
    # Wrapper should include client metadata when context is available
    assert parsed["dimension1"] == ["failing_tool"]
    assert parsed["dimension2"] == ["error"]
    # Error message is included
    assert parsed["dimension4"] == ["boom"]
    assert parsed["dimension5"] == ["unknown"]
    assert parsed["dimension6"] == ["unknown"]
