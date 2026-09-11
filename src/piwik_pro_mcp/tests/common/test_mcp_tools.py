"""Tests for MCP tool thread-pool wrapping."""

from __future__ import annotations

import asyncio
import time

import pytest
from mcp.server.fastmcp import FastMCP

from piwik_pro_mcp.common.mcp_tools import (
    reset_tool_executor_for_tests,
    run_sync_tool,
    tool_thread_pool_max_workers,
    wrap_sync_tools_in_thread_pool,
)
from piwik_pro_mcp.common.settings import safe_mode_enabled
from piwik_pro_mcp.server import create_mcp_server


@pytest.fixture(autouse=True)
def _reset_tool_executor():
    yield
    reset_tool_executor_for_tests()


class TestToolThreadPoolMaxWorkers:
    def test_default_max_workers(self, monkeypatch):
        monkeypatch.delenv("PIWIK_PRO_TOOL_MAX_WORKERS", raising=False)
        assert tool_thread_pool_max_workers() >= 1

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("PIWIK_PRO_TOOL_MAX_WORKERS", "8")
        assert tool_thread_pool_max_workers() == 8

    def test_rejects_invalid_value(self, monkeypatch):
        monkeypatch.setenv("PIWIK_PRO_TOOL_MAX_WORKERS", "abc")
        with pytest.raises(ValueError, match="integer"):
            tool_thread_pool_max_workers()


class TestWrapSyncToolsInThreadPool:
    async def test_wraps_sync_tools_as_async(self):
        mcp = FastMCP("test")

        @mcp.tool()
        def sync_tool(value: int) -> int:
            return value + 1

        assert wrap_sync_tools_in_thread_pool(mcp) == 1

        tool = mcp._tool_manager.get_tool("sync_tool")
        assert tool is not None
        assert tool.is_async is True

        result = await mcp.call_tool("sync_tool", {"value": 41})
        assert isinstance(result, tuple) and len(result) == 2
        _, data = result
        assert data["result"] == 42

    async def test_concurrent_sync_tools_do_not_block_event_loop(self):
        mcp = FastMCP("test")

        @mcp.tool()
        def slow_tool() -> str:
            time.sleep(0.15)
            return "done"

        wrap_sync_tools_in_thread_pool(mcp)

        start = time.monotonic()
        await asyncio.gather(
            mcp.call_tool("slow_tool", {}),
            mcp.call_tool("slow_tool", {}),
        )
        elapsed = time.monotonic() - start

        assert elapsed < 0.28

    async def test_run_sync_tool_executes_callable(self):
        def add(a: int, b: int) -> int:
            return a + b

        assert await run_sync_tool(add, 2, 3) == 5


class TestCreateMcpServerToolWrapping:
    async def test_all_registered_tools_are_async(self, mcp_server):
        tools = mcp_server._tool_manager._tools.values()
        assert tools
        assert all(tool.is_async for tool in tools)

    async def test_create_mcp_server_wraps_expected_tool_count(self, mcp_server):
        assert len(mcp_server._tool_manager._tools) >= 60

    async def test_safe_mode_server_still_wraps_remaining_tools(self, monkeypatch):
        monkeypatch.setenv("PIWIK_PRO_SAFE_MODE", "1")

        safe_mode_enabled.cache_clear()
        server = create_mcp_server()
        safe_mode_enabled.cache_clear()

        tools = server._tool_manager._tools.values()
        assert tools
        assert all(tool.is_async for tool in tools)
