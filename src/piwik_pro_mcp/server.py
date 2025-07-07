#!/usr/bin/env python3
"""
MCP Piwik PRO Analytics Server using FastMCP

An MCP server that provides tools for interacting with Piwik PRO analytics API.
Authentication is handled via client credentials from environment variables.

Usage:
    python server.py [--env-file ENV_FILE]

Options:
    --env-file: Path to .env file to load environment variables from
"""

import argparse
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from piwik_pro_mcp.common.telemetry import TelemetrySender

from .common import mcp_telemetry_wrapper
from .tools import register_all_tools


def create_mcp_server() -> FastMCP:
    """Create and configure the FastMCP server with all Piwik PRO tools."""
    mcp = FastMCP("Piwik PRO Analytics Server 📊")

    # Instrument MCP with telemetry before registering any tools
    if os.getenv("PIWIK_PRO_TELEMETRY", "1") == "1":
        mcp_telemetry_wrapper(mcp, TelemetrySender(endpoint_url="https://success.piwik.pro/ppms.php"))

    # Register all tool modules
    register_all_tools(mcp)

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
server = create_mcp_server()


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


def start_server():
    """Start the server in STDIO mode for MCP client connections."""
    logger.info("Starting MCP Piwik PRO Analytics Server... 🚀")
    logger.debug("Required environment variables: PIWIK_PRO_HOST, PIWIK_PRO_CLIENT_ID, PIWIK_PRO_CLIENT_SECRET")
    validate_environment()
    if os.getenv("PIWIK_PRO_TELEMETRY", "1") == "0":
        logger.info("Telemetry: Disabled 📡")
    logger.info("Server ready for MCP client connections 🎉")
    logger.info("Press Ctrl+C to stop the server")

    try:
        server.run()
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

    args = parser.parse_args()

    # Load environment variables from file if specified
    if args.env_file:
        load_env_file(args.env_file)

    start_server()


if __name__ == "__main__":
    main()
