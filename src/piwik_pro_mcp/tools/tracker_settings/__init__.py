"""
Tracker settings tools for Piwik PRO MCP server.

This module provides MCP tools for managing Piwik PRO tracker settings
including global and app-specific settings.
"""

from .tools import register_tracker_settings_tools

__all__ = [
    "register_tracker_settings_tools",
]
