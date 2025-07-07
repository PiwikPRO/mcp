"""
CDP (Customer Data Platform) tools for Piwik PRO MCP server.

This module provides MCP tools for managing Piwik PRO CDP audiences including
creation, listing, and retrieval of audiences.
"""

from .tools import register_cdp_tools

__all__ = [
    "register_cdp_tools",
]
