"""
Template discovery tools for Tag Manager.

This module provides MCP tools for discovering and retrieving information
about available templates for tags, triggers, and variables.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP

from piwik_pro_mcp.common.templates import (
    list_available_assets,
    load_tag_template_with_extends,
    load_trigger_template_with_extends,
    load_variable_template_with_extends,
    resolve_whitelisted_template_path,
)


def get_tag_template(template_name: str) -> dict[str, Any]:
    try:
        template_file = resolve_whitelisted_template_path("tag_manager/tags", template_name)
        return load_tag_template_with_extends(template_file)

    except Exception as e:
        raise RuntimeError(f"Failed to get tag template information: {str(e)}")


def get_available_tag_templates() -> dict[str, Any]:
    try:
        available_assets = list_available_assets("tag_manager/tags")

        return {
            "available_templates": available_assets,
            "total_count": len(available_assets),
            "usage_guide": {
                "next_steps": [
                    "Use get_tag_template(template_name='TEMPLATE_NAME') to get detailed information "
                    "about a specific template",
                    "Use tags_create() with the template information to create tags",
                ],
                "example_workflow": {
                    "step_1": "get_available_tag_templates() - See all available templates",
                    "step_2": "get_tag_template(template_name='custom_tag') - Get details for a specific template",
                    "step_3": "tags_create(app_id='...', attributes={...}) - Create the tag with proper attributes",
                },
            },
            "note": "Each template provides comprehensive documentation including required attributes, "
            "examples, and best practices optimized for AI usage",
        }

    except Exception as e:
        raise RuntimeError(f"Failed to list available templates: {str(e)}")


def get_trigger_template(template_name: str) -> dict[str, Any]:
    try:
        template_file = resolve_whitelisted_template_path(
            "tag_manager/triggers",
            template_name,
            resource_label="Trigger template",
        )
        return load_trigger_template_with_extends(template_file)

    except Exception as e:
        raise RuntimeError(f"Failed to get trigger template information: {str(e)}")


def get_available_trigger_templates() -> dict[str, Any]:
    try:
        available_assets = list_available_assets("tag_manager/triggers")

        return {
            "available_templates": available_assets,
            "total_count": len(available_assets),
            "usage_guide": {
                "next_steps": [
                    "Use get_trigger_template(template_name='TEMPLATE_NAME') to get detailed information "
                    "about a specific trigger template",
                    "Use triggers_create() with the template information to create triggers",
                ],
                "example_workflow": {
                    "step_1": "get_available_trigger_templates() - See all available trigger templates",
                    "step_2": "get_trigger_template(template_name='page_view') - "
                    "Get details for a specific trigger template",
                    "step_3": "triggers_create(app_id='...', attributes={...}) - "
                    "Create the trigger with proper attributes",
                },
            },
            "note": "Each trigger template provides comprehensive documentation including required attributes, "
            "examples, and best practices optimized for AI usage",
        }

    except Exception as e:
        raise RuntimeError(f"Failed to list available trigger templates: {str(e)}")


def get_variable_template(template_name: str) -> dict[str, Any]:
    try:
        template_file = resolve_whitelisted_template_path(
            "tag_manager/variables",
            template_name,
            resource_label="Variable template",
        )
        return load_variable_template_with_extends(template_file)

    except Exception as e:
        raise RuntimeError(f"Failed to get variable template information: {str(e)}")


def get_available_variable_templates() -> dict[str, Any]:
    try:
        available_assets = list_available_assets("tag_manager/variables")

        return {
            "available_templates": available_assets,
            "total_count": len(available_assets),
            "usage_guide": {
                "discovery_workflow": [
                    "Use get_variable_template(template_name='TEMPLATE_NAME') to get detailed information "
                    "about a specific variable template with field mutability guidance",
                    "Use variables_create() with the template information to create variables",
                    "Use variables_update() with the template information to update variables "
                    "(only editable fields processed)",
                ],
                "create_update_workflow": {
                    "step_1": "get_available_variable_templates() - See all available variable templates",
                    "step_2": "get_variable_template(template_name='data_layer') - "
                    "Get complete create/update template info",
                    "step_3": "variables_create(app_id='...', attributes={...}) - "
                    "Create variable with proper attributes",
                    "step_4": "variables_update(app_id='...', variable_id='...', attributes={...}) - "
                    "Update with editable fields only",
                },
                "field_mutability": {
                    "editable": "✅ For variables_update only (e.g., name, is_active, template options). Do NOT include in variables_create.",  # noqa: E501
                    "create_only": "⚠️ Set during creation, immutable after (variable_type)",
                    "read_only": "🚫 Auto-generated, never user-modifiable (created_at, updated_at)",
                },
            },
            "note": "Each variable template provides comprehensive documentation including required attributes, "
            "field mutability information, examples, and best practices optimized for AI usage in both "
            "create and update scenarios",
        }

    except Exception as e:
        raise RuntimeError(f"Failed to list available variable templates: {str(e)}")


def register_template_tools(mcp: FastMCP) -> None:
    """Register all template discovery tools with the MCP server."""

    @mcp.tool(annotations={"title": "Piwik PRO: List Tag Templates", "readOnlyHint": True})
    def templates_list_tags() -> dict:
        """List all available tag templates for use with tags_create.

        ⚠️ IMPORTANT: You MUST call this tool before calling templates_get_tag() or tags_create()
        to discover exact template names. Do NOT guess template names.

        Workflow:
            1. templates_list_tags() → get exact template names
            2. templates_get_tag(template_name='...') → get requirements for chosen template
            3. tags_create() → create the tag
        """
        return get_available_tag_templates()

    @mcp.tool(annotations={"title": "Piwik PRO: Get Tag Template", "readOnlyHint": True})
    def templates_get_tag(template_name: str) -> dict:
        """Get requirements and usage details for a specific tag template.

        ⚠️ IMPORTANT: You MUST call templates_list_tags() first to get exact template names.
        Do NOT guess template names — use only names returned by templates_list_tags().

        Args:
            template_name: Exact template name as returned by templates_list_tags()

        Workflow:
            1. templates_list_tags() → get exact template names
            2. templates_get_tag(template_name='...') → get requirements (this tool)
            3. tags_create() → create the tag
        """
        return get_tag_template(template_name)

    @mcp.tool(annotations={"title": "Piwik PRO: List Trigger Templates", "readOnlyHint": True})
    def templates_list_triggers() -> dict:
        """List all available trigger templates for use with triggers_create.

        ⚠️ IMPORTANT: You MUST call this tool before calling templates_get_trigger() or triggers_create()
        to discover exact trigger type names. Do NOT guess trigger type names.

        Workflow:
            1. templates_list_triggers() → get exact trigger type names
            2. templates_get_trigger(template_name='...') → get requirements for chosen type
            3. triggers_create() → create the trigger
        """
        return get_available_trigger_templates()

    @mcp.tool(annotations={"title": "Piwik PRO: Get Trigger Template", "readOnlyHint": True})
    def templates_get_trigger(template_name: str) -> dict:
        """Get requirements and usage details for a specific trigger template.

        ⚠️ IMPORTANT: You MUST call templates_list_triggers() first to get exact trigger type names.
        Do NOT guess trigger type names — use only names returned by templates_list_triggers().

        Args:
            template_name: Exact trigger type name as returned by templates_list_triggers()

        Workflow:
            1. templates_list_triggers() → get exact trigger type names
            2. templates_get_trigger(template_name='...') → get requirements (this tool)
            3. triggers_create() → create the trigger
        """
        return get_trigger_template(template_name)

    @mcp.tool(annotations={"title": "Piwik PRO: List Variable Templates", "readOnlyHint": True})
    def templates_list_variables() -> dict:
        """List all available variable templates for use with variables_create and variables_update.

        ⚠️ IMPORTANT: You MUST call this tool before calling templates_get_variable() or variables_create()
        to discover exact variable type names. Do NOT guess variable type names.

        Workflow:
            1. templates_list_variables() → get exact variable type names
            2. templates_get_variable(template_name='...') → get requirements for chosen type
            3. variables_create() or variables_update() → create/update the variable
        """
        return get_available_variable_templates()

    @mcp.tool(annotations={"title": "Piwik PRO: Get Variable Template", "readOnlyHint": True})
    def templates_get_variable(template_name: str) -> dict:
        """Get requirements, field mutability, and usage details for a specific variable template.

        ⚠️ IMPORTANT: You MUST call templates_list_variables() first to get exact variable type names.
        Do NOT guess variable type names — use only names returned by templates_list_variables().

        Args:
            template_name: Exact variable type name as returned by templates_list_variables()

        Workflow:
            1. templates_list_variables() → get exact variable type names
            2. templates_get_variable(template_name='...') → get requirements (this tool)
            3. variables_create() or variables_update() → create/update the variable
        """
        return get_variable_template(template_name)
