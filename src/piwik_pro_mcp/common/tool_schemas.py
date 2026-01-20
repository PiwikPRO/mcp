"""
Tool parameter schemas.

This module provides a simple mapping of tool names to their parameter models,
following Python's principle of explicit over implicit.
"""

from typing import Any, Dict, Type

from pydantic import BaseModel

from piwik_pro_mcp.api.methods.analytics.models import QueryRequest
from piwik_pro_mcp.api.methods.apps.models import AppEditableAttributes, NewAppAttributes
from piwik_pro_mcp.api.methods.cdp.models import EditableAudienceAttributes, NewAudienceAttributes
from piwik_pro_mcp.api.methods.tag_manager.models import TagFilters, TriggerAttributes, TriggerFilters, VariableFilters
from piwik_pro_mcp.api.methods.tracker_settings.models import AppTrackerSettings, GlobalTrackerSettings

from ..tools.tag_manager.models import (
    TagManagerCreateAttributes,
    TagManagerUpdateAttributes,
    VariableCreateAttributes,
    VariableUpdateAttributes,
)

TOOL_PARAMETER_MODELS: Dict[str, Type[BaseModel]] = {
    "apps_create": NewAppAttributes,
    "apps_update": AppEditableAttributes,
    "audiences_create": NewAudienceAttributes,
    "audiences_update": EditableAudienceAttributes,
    "tracker_settings_app_update": AppTrackerSettings,
    "tracker_settings_global_update": GlobalTrackerSettings,
    "tags_create": TagManagerCreateAttributes,
    "tags_update": TagManagerUpdateAttributes,
    "tags_list": TagFilters,
    "triggers_create": TriggerAttributes,
    "triggers_list": TriggerFilters,
    "variables_create": VariableCreateAttributes,
    "variables_update": VariableUpdateAttributes,
    "variables_list": VariableFilters,
    "analytics_query_execute": QueryRequest,
}


def get_tool_schema(tool_name: str) -> Dict[str, Any]:
    """
    Get JSON schema for a tool's parameters.

    Args:
        tool_name: Name of the MCP tool

    Returns:
        JSON schema dictionary for the tool's parameters

    Raises:
        ValueError: If tool_name is not recognized
    """
    if tool_name not in TOOL_PARAMETER_MODELS:
        raise ValueError(f"Unknown tool: {tool_name}")

    schema = TOOL_PARAMETER_MODELS[tool_name].model_json_schema()

    return schema


def get_all_registered_tools() -> list[str]:
    """Get list of all registered tool names."""
    return list(TOOL_PARAMETER_MODELS.keys())
