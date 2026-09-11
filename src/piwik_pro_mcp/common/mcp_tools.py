"""
Helpers for registering MCP tools that must not block the asyncio event loop.

Sync tool handlers and their blocking HTTP clients are offloaded to a dedicated
thread pool so concurrent HTTP MCP requests and ``/health`` stay responsive.
"""

from __future__ import annotations

import asyncio
import functools
import os
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from mcp.server.fastmcp import FastMCP


class _ToolExecutorHolder:
    executor: ThreadPoolExecutor | None = None


def _default_max_workers() -> int:
    cpu_count = os.cpu_count() or 1
    return min(32, cpu_count + 4)


def tool_thread_pool_max_workers() -> int:
    """Return configured max workers for the MCP tool thread pool."""

    value = os.getenv("PIWIK_PRO_TOOL_MAX_WORKERS")
    if value is None:
        return _default_max_workers()

    normalized = value.strip()
    if not normalized:
        return _default_max_workers()

    try:
        max_workers = int(normalized)
    except ValueError as exc:
        raise ValueError("PIWIK_PRO_TOOL_MAX_WORKERS must be an integer") from exc

    if max_workers < 1:
        raise ValueError("PIWIK_PRO_TOOL_MAX_WORKERS must be at least 1")

    return max_workers


def _get_tool_executor() -> ThreadPoolExecutor:
    if _ToolExecutorHolder.executor is None:
        _ToolExecutorHolder.executor = ThreadPoolExecutor(
            max_workers=tool_thread_pool_max_workers(),
            thread_name_prefix="piwik-mcp-tool",
        )
    return _ToolExecutorHolder.executor


def reset_tool_executor_for_tests() -> None:
    """Shut down and clear the shared executor (test helper)."""

    if _ToolExecutorHolder.executor is not None:
        _ToolExecutorHolder.executor.shutdown(wait=False, cancel_futures=True)
        _ToolExecutorHolder.executor = None


async def run_sync_tool(fn: Callable[..., Any], /, *args: Any, **kwargs: Any) -> Any:
    """Run a blocking tool handler in the shared thread pool."""

    loop = asyncio.get_running_loop()
    bound = functools.partial(fn, *args, **kwargs)
    return await loop.run_in_executor(_get_tool_executor(), bound)


def wrap_sync_tools_in_thread_pool(mcp: FastMCP) -> int:
    """Wrap every registered sync MCP tool so it runs in the thread pool.

    Returns:
        Number of tools wrapped.
    """

    wrapped_count = 0

    for name, tool in list(mcp._tool_manager._tools.items()):
        if tool.is_async:
            continue

        sync_fn = tool.fn

        @functools.wraps(sync_fn)
        async def async_runner(*args: Any, _sync_fn: Callable[..., Any] = sync_fn, **kwargs: Any) -> Any:
            return await run_sync_tool(_sync_fn, *args, **kwargs)

        mcp._tool_manager._tools[name] = tool.model_copy(update={"fn": async_runner, "is_async": True})
        wrapped_count += 1

    return wrapped_count
