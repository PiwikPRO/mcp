"""
App management tools for Piwik PRO MCP server.

This module provides MCP tools for managing Piwik PRO apps including
creation, updating, listing, and deletion of apps.
"""

from .tools import register_app_tools

__all__ = [
    "register_app_tools",
]
