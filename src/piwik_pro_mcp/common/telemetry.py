"""
Telemetry collection and sending utilities for MCP tools.

This module provides:
- TelemetryEvent: Pydantic model describing a tool invocation event
- TelemetrySender: Async HTTP sender with safe background dispatching
- instrument_mcp_with_telemetry: Wraps FastMCP.tool to auto-collect telemetry
"""

from __future__ import annotations

import asyncio
import inspect
import threading
import time
import uuid
from enum import Enum
from functools import wraps
from typing import Any, Callable, Optional
from urllib.parse import quote_plus

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field


class TelemetryStatus(str, Enum):
    """Enumeration of possible tool invocation outcomes."""

    SUCCESS = "success"
    ERROR = "error"


class TelemetryEvent(BaseModel):
    """Telemetry event describing a single MCP tool invocation.

    Args:
        tool_name: Name of the invoked tool (function name)
        status: Outcome of the invocation (success or error)
        duration_ms: Execution duration in milliseconds
        error_message: Optional error detail when status is error
        metadata: Optional additional context (kept minimal by default)

    Note: Keep payload small to avoid leaking user data. Do not include
    tool inputs or outputs unless explicitly approved.
    """

    tool_name: str = Field(alias="dimension1")
    status: TelemetryStatus = Field(alias="dimension2")
    duration_ms: int = Field(ge=0, alias="dimension3")
    error_message: Optional[str] = Field(alias="dimension4")
    rec: int = Field(alias="rec", default=1)
    client_name: str = Field(alias="dimension5")
    client_version: str = Field(alias="dimension6")
    id_site: str = Field(alias="idsite", default="f0af09a5-bb2c-410e-a074-5ff3fff38ad2")
    action_name: str = Field(alias="action_name", default="mcp_tool_call")
    event_category: str = Field(alias="e_c", default="MCP")
    event_action: str = Field(alias="e_a", default="mcp_tool_call")
    event_name: str = Field(alias="e_n")
    event_value: int = Field(alias="e_v", default=1)
    visitor_id: str = Field(alias="_id")

    # Allow population by field names while keeping aliases for serialization
    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)


class TelemetrySender:
    """Asynchronous HTTP sender for telemetry events.

    The sender is resilient and non-blocking: failures are swallowed and
    requests are dispatched in the background so tool execution is not delayed.
    """

    def __init__(
        self,
        endpoint_url: Optional[str],
        timeout_seconds: float = 2.0,
        enabled: bool = True,
    ) -> None:
        """Initialize the sender.

        Args:
            endpoint_url: Target URL to POST telemetry JSON to
            timeout_seconds: Per-request timeout
            enabled: Global enable/disable flag
        """
        self.endpoint_url = endpoint_url
        self.timeout_seconds = timeout_seconds
        self.enabled = enabled and bool(endpoint_url)

    async def send_event(self, event: TelemetryEvent) -> None:
        """Send a telemetry event asynchronously.

        Swallows exceptions to avoid impacting tool execution.
        """
        if not self.enabled or not self.endpoint_url:
            return

        headers = {"Content-Type": "application/json"}

        dumped_event = event.model_dump(by_alias=True, exclude_none=True)
        event_query_params = "&".join(
            [f"{quote_plus(key)}={quote_plus(str(value))}" for key, value in dumped_event.items()]
        )
        event_payload = {"requests": ["?" + event_query_params]}

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                await client.post(self.endpoint_url, json=event_payload, headers=headers)
        except Exception:
            # Intentionally swallow all errors
            return

    def send_event_in_background(self, event: TelemetryEvent) -> None:
        """Dispatch the send task without blocking the caller.

        If an event loop is running, schedule via create_task; otherwise run
        in a background daemon thread using asyncio.run.
        """
        if not self.enabled or not self.endpoint_url:
            return

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            try:
                loop.create_task(self.send_event(event))
                return
            except Exception:
                # Fallback to thread if scheduling fails
                pass

        def _runner() -> None:
            try:
                asyncio.run(self.send_event(event))
            except Exception:
                return

        thread = threading.Thread(target=_runner, daemon=True)
        thread.start()


def mcp_telemetry_wrapper(mcp: FastMCP, sender: TelemetrySender) -> None:
    """Monkey-patch FastMCP.tool to wrap all registered tools with telemetry.

    This must be called before registering any tools on the provided `mcp`.

    Args:
        mcp: FastMCP instance to instrument
        sender: TelemetrySender instance to use for sending events
    """
    original_tool = mcp.tool
    visitor_id = uuid.uuid4().hex[:16]

    def tool_with_telemetry(*t_args: Any, **t_kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        decorator = original_tool(*t_args, **t_kwargs)

        def _decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            tool_name = getattr(func, "__name__", "unknown_tool")

            @wraps(func)
            def _wrapped(*args: Any, **kwargs: Any) -> Any:
                start = time.perf_counter()

                try:
                    ctx = mcp.get_context()
                    client_name = "unknown"
                    client_version = "unknown"
                    if ctx is not None:
                        clientInfo = ctx.session.client_params.clientInfo
                        client_name = clientInfo.name if clientInfo.name else "unknown"
                        client_version = clientInfo.version if clientInfo.version else "unknown"
                except Exception:
                    client_name = "unknown"
                    client_version = "unknown"

                try:
                    result = func(*args, **kwargs)
                    status = TelemetryStatus.SUCCESS
                    error_message = None
                    return result
                except Exception as exc:  # noqa: BLE001
                    status = TelemetryStatus.ERROR
                    error_message = str(exc)
                    raise
                finally:
                    duration_ms = int((time.perf_counter() - start) * 1000)
                    event = TelemetryEvent(
                        tool_name=tool_name,
                        status=status,
                        duration_ms=duration_ms,
                        error_message=error_message,
                        client_name=client_name,
                        client_version=client_version,
                        event_category="MCP",
                        event_action=tool_name,
                        event_name=tool_name,
                        event_value=int(TelemetryStatus.SUCCESS != status),
                        visitor_id=visitor_id,
                    )
                    sender.send_event_in_background(event)

            # Preserve the original call signature for FastMCP's introspection
            try:
                _wrapped.__signature__ = inspect.signature(func)  # type: ignore[attr-defined]
            except (ValueError, TypeError):
                pass

            return decorator(_wrapped)

        return _decorator

    # Attach the new method to this instance
    setattr(mcp, "tool", tool_with_telemetry)
