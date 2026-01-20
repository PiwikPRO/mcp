#!/usr/bin/env python3
"""
MCP Piwik PRO Analytics Server using FastMCP

An MCP server that provides tools for interacting with Piwik PRO analytics API.
Authentication is handled via client credentials from environment variables.

Usage:
    python server.py [--env-file ENV_FILE] [--transport TRANSPORT] [--host HOST] [--port PORT] [--path PATH]

Options:
    --env-file: Path to .env file to load environment variables from
    --transport: Transport to expose the MCP server (stdio, streamable-http)
    --host: Host to bind when using streamable-http transport (default: 0.0.0.0)
    --port: Port to bind when using streamable-http transport (default: 8000)
    --path: Path for the streamable-http transport endpoint (default: /mcp)
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Literal, Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from piwik_pro_mcp.common.settings import safe_mode_enabled, telemetry_enabled
from piwik_pro_mcp.common.telemetry import TelemetrySender

from .common import mcp_telemetry_wrapper
from .tools import filter_write_tools, register_all_tools


def create_mcp_server() -> FastMCP:
    """Create and configure the FastMCP server with all Piwik PRO tools."""
    mcp = FastMCP("Piwik PRO Analytics Server 📊")

    # Instrument MCP with telemetry before registering any tools
    if telemetry_enabled():
        mcp_telemetry_wrapper(mcp, TelemetrySender(endpoint_url="https://success.piwik.pro/ppms.php"))

    # Register all tool modules
    register_all_tools(mcp)

    # Filter out write tools when safe mode is enabled
    if safe_mode_enabled():
        removed_count = filter_write_tools(mcp)
        logger.info("Safe mode: Removed %d write tools, keeping read-only tools only", removed_count)

    return mcp


def _configure_logging_from_env() -> None:
    """Configure root logging from environment variables.

    Respects:
      - LOG_LEVEL: Python logging level name (DEBUG, INFO, WARNING, ERROR, CRITICAL). Defaults to INFO.
    """
    # Avoid re-configuring if handlers already exist
    if logging.getLogger().handlers:
        return

    log_level_name = os.getenv("LOG_LEVEL", "INFO").upper().strip()
    level = getattr(logging, log_level_name, logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(message)s",
    )


_configure_logging_from_env()

logger = logging.getLogger(__name__)


def load_env_file(env_file_path):
    """Load environment variables from a .env file."""
    if not env_file_path:
        return

    env_path = Path(env_file_path)
    if not env_path.exists():
        logger.error("Environment file not found: %s", env_file_path)
        sys.exit(1)

    try:
        load_dotenv(env_path)
        logger.info("Loaded environment variables from: %s", env_file_path)

        # Clear cached settings so they re-read from updated environment
        safe_mode_enabled.cache_clear()
        telemetry_enabled.cache_clear()
    except ImportError:
        logger.error("python-dotenv not installed. Install with: pip install python-dotenv")
        sys.exit(1)
    except Exception as e:
        logger.exception("Error loading environment file: %s", e)
        sys.exit(1)


def validate_environment():
    """Validate that required environment variables are set."""
    required_vars = ["PIWIK_PRO_HOST", "PIWIK_PRO_CLIENT_ID", "PIWIK_PRO_CLIENT_SECRET"]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        logger.error("Missing required environment variables: %s", ", ".join(missing_vars))
        logger.error("Either set these in your environment or use --env-file to load from a .env file")
        sys.exit(1)


DEFAULT_HTTP_HOST = "0.0.0.0"
DEFAULT_HTTP_PORT = 8000
DEFAULT_HTTP_PATH = "/mcp"

CliTransport = Literal["stdio", "streamable-http"]


def _normalize_path(path_value: str) -> str:
    if not path_value.startswith("/"):
        return f"/{path_value}"
    return path_value


def start_server(
    transport: CliTransport = "stdio",
    host: Optional[str] = None,
    port: Optional[int] = None,
    path: Optional[str] = None,
) -> None:
    """Start the MCP server using the requested transport."""
    logger.info("Starting MCP Piwik PRO Analytics Server... 🚀")
    logger.debug("Required environment variables: PIWIK_PRO_HOST, PIWIK_PRO_CLIENT_ID, PIWIK_PRO_CLIENT_SECRET")
    validate_environment()

    if not telemetry_enabled():
        logger.info("Telemetry: Disabled 📡")

    if safe_mode_enabled():
        logger.info("Safe Mode: Enabled (read-only tools only) 🔒")

    # Create server instance (after env is fully loaded)
    server = create_mcp_server()

    if transport == "streamable-http":
        resolved_host = host or DEFAULT_HTTP_HOST
        resolved_port = port or DEFAULT_HTTP_PORT
        resolved_path = path or DEFAULT_HTTP_PATH
        resolved_path = _normalize_path(resolved_path)

        server.settings.host = resolved_host
        server.settings.port = resolved_port
        server.settings.streamable_http_path = resolved_path

        logger.info("Streamable HTTP transport enabled: http://%s:%s%s", resolved_host, resolved_port, resolved_path)
    else:
        logger.info("STDIO transport enabled (default) 🔌")

    logger.info("Server ready for MCP client connections 🎉")
    logger.info("Press Ctrl+C to stop the server")

    try:
        server.run(transport=transport)
    except KeyboardInterrupt:
        logger.info("Server stopped gracefully")
    except Exception as e:
        logger.exception("Error starting server: %s", e)
        sys.exit(1)


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="MCP Piwik PRO Analytics Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python server.py                           # Start server
  python server.py --env-file .env           # Load environment variables from .env file
  python server.py --env-file /path/to/.env  # Load from specific .env file path
  python server.py --transport streamable-http --port 8080  # Expose over HTTP(S) on port 8080

Required environment variables:
  PIWIK_PRO_HOST         - Your Piwik PRO instance hostname
  PIWIK_PRO_CLIENT_ID    - OAuth client ID
  PIWIK_PRO_CLIENT_SECRET - OAuth client secret

Environment file format (.env):
  PIWIK_PRO_HOST=your-instance.piwik.pro
  PIWIK_PRO_CLIENT_ID=your-client-id
  PIWIK_PRO_CLIENT_SECRET=your-client-secret
        """,
    )

    parser.add_argument(
        "--env-file",
        type=str,
        help="Path to .env file to load environment variables from",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "http", "streamable-http"],
        default="stdio",
        help="Transport to expose the MCP server (default: stdio, use streamable-http for HTTP transport)",
    )
    parser.add_argument(
        "--host",
        type=str,
        help=f"Host to bind when using streamable-http transport (default: {DEFAULT_HTTP_HOST})",
    )
    parser.add_argument(
        "--port",
        type=int,
        help=f"Port to bind when using streamable-http transport (default: {DEFAULT_HTTP_PORT})",
    )
    parser.add_argument(
        "--path",
        type=str,
        help=f"Path for streamable-http transport endpoint (default: {DEFAULT_HTTP_PATH})",
    )

    args = parser.parse_args()

    # Load environment variables from file if specified
    if args.env_file:
        load_env_file(args.env_file)

    if args.transport not in {"http", "streamable-http"} and any(
        value is not None for value in (args.host, args.port, args.path)
    ):
        parser.error("--host, --port, and --path can only be used with --transport http or streamable-http")

    start_server(
        transport=args.transport,
        host=args.host,
        port=args.port,
        path=args.path,
    )


if __name__ == "__main__":
    main()
