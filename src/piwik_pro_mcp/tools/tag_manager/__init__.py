"""
Tag Manager tools for Piwik PRO MCP server.

This module provides comprehensive MCP tools for managing Piwik PRO Tag Manager
including tags, triggers, variables, versions, and template discovery.
"""

from .tags import register_tag_tools
from .templates import register_template_tools
from .triggers import register_trigger_tools
from .variables import register_variable_tools
from .versions import register_version_tools

__all__ = [
    "register_tag_tools",
    "register_trigger_tools",
    "register_variable_tools",
    "register_version_tools",
    "register_template_tools",
]
