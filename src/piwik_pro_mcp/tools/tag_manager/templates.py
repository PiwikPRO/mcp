"""
Template discovery tools for Tag Manager.

This module provides MCP tools for discovering and retrieving information
about available templates for tags, triggers, and variables.
"""

from pathlib import Path
from typing import Any, Dict

from mcp.server.fastmcp import FastMCP

from piwik_pro_mcp.common.templates import (
    get_assets_base_path,
    list_template_names,
    load_template_asset,
)


def get_tag_template(template_name: str) -> Dict[str, Any]:
    try:
        assets_dir: Path = get_assets_base_path() / "tag_manager" / "tags"
        template_file: Path = assets_dir / f"{template_name}.json"

        if not template_file.exists():
            available_templates = list_template_names(assets_dir)
            available_msg = f" Available templates: {', '.join(available_templates)}" if available_templates else ""
            raise RuntimeError(f"Template '{template_name}' not found.{available_msg}")

        return load_template_asset(template_file)

    except Exception as e:
        raise RuntimeError(f"Failed to get tag template information: {str(e)}")


def get_available_templates() -> Dict[str, Any]:
    try:
        template_names = list_template_names("tag_manager/tags")

        return {
            "available_templates": template_names,
            "total_count": len(template_names),
            "usage_guide": {
                "next_steps": [
                    "Use get_tag_template(template_name='TEMPLATE_NAME') to get detailed information "
                    "about a specific template",
                    "Use create_tag() with the template information to create tags",
                ],
                "example_workflow": {
                    "step_1": "get_available_templates() - See all available templates",
                    "step_2": "get_tag_template(template_name='custom_tag') - Get details for a specific template",
                    "step_3": "create_tag(app_id='...', attributes={...}) - Create the tag with proper attributes",
                },
            },
            "note": "Each template provides comprehensive documentation including required attributes, "
            "examples, and best practices optimized for AI usage",
        }

    except Exception as e:
        raise RuntimeError(f"Failed to list available templates: {str(e)}")


def get_trigger_template(template_name: str) -> Dict[str, Any]:
    try:
        assets_dir: Path = get_assets_base_path() / "tag_manager" / "triggers"
        template_file: Path = assets_dir / f"{template_name}.json"

        if not template_file.exists():
            available_templates = list_template_names(assets_dir)
            available_msg = (
                f" Available trigger templates: {', '.join(available_templates)}" if available_templates else ""
            )
            raise RuntimeError(f"Trigger template '{template_name}' not found.{available_msg}")

        return load_template_asset(template_file)

    except Exception as e:
        raise RuntimeError(f"Failed to get trigger template information: {str(e)}")


def get_available_trigger_templates() -> Dict[str, Any]:
    try:
        template_names = list_template_names("tag_manager/triggers")

        return {
            "available_templates": template_names,
            "total_count": len(template_names),
            "usage_guide": {
                "next_steps": [
                    "Use get_trigger_template(template_name='TEMPLATE_NAME') to get detailed information "
                    "about a specific trigger template",
                    "Use create_trigger() with the template information to create triggers",
                ],
                "example_workflow": {
                    "step_1": "get_available_trigger_templates() - See all available trigger templates",
                    "step_2": "get_trigger_template(template_name='page_view') - "
                    "Get details for a specific trigger template",
                    "step_3": "create_trigger(app_id='...', attributes={...}) - "
                    "Create the trigger with proper attributes",
                },
            },
            "note": "Each trigger template provides comprehensive documentation including required attributes, "
            "examples, and best practices optimized for AI usage",
        }

    except Exception as e:
        raise RuntimeError(f"Failed to list available trigger templates: {str(e)}")


def get_variable_template(template_name: str) -> Dict[str, Any]:
    try:
        assets_dir: Path = get_assets_base_path() / "tag_manager" / "variables"
        template_file: Path = assets_dir / f"{template_name}.json"

        if not template_file.exists():
            available_templates = list_template_names(assets_dir)
            available_msg = (
                f" Available variable templates: {', '.join(available_templates)}" if available_templates else ""
            )
            raise RuntimeError(f"Variable template '{template_name}' not found.{available_msg}")

        return load_template_asset(template_file)

    except Exception as e:
        raise RuntimeError(f"Failed to get variable template information: {str(e)}")


def get_available_variable_templates() -> Dict[str, Any]:
    try:
        template_names = list_template_names("tag_manager/variables")

        return {
            "available_templates": template_names,
            "total_count": len(template_names),
            "usage_guide": {
                "discovery_workflow": [
                    "Use get_variable_template(template_name='TEMPLATE_NAME') to get detailed information "
                    "about a specific variable template with field mutability guidance",
                    "Use create_variable() with the template information to create variables",
                    "Use update_variable() with the template information to update variables "
                    "(only editable fields processed)",
                ],
                "create_update_workflow": {
                    "step_1": "get_available_variable_templates() - See all available variable templates",
                    "step_2": "get_variable_template(template_name='data_layer') - "
                    "Get complete create/update template info",
                    "step_3": "create_variable(app_id='...', attributes={...}) - "
                    "Create variable with proper attributes",
                    "step_4": "update_variable(app_id='...', variable_id='...', attributes={...}) - "
                    "Update with editable fields only",
                },
                "field_mutability": {
                    "editable": "✅ Can be updated anytime (name, is_active, template options)",
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
    def templates_list() -> dict:
        """List all available Piwik PRO Tag Manager templates.

        This tool returns a list of all available tag templates that can be used with tags_create.
        Each template has detailed documentation available via templates_get_tag.

        Returns:
            Dictionary containing:
            - available_templates: List of template names
            - total_count: Number of available templates
            - usage_guide: Instructions on how to use templates
            - note: Information about template documentation

        Examples:
            # Get list of all available templates
            templates = templates_list()

            # Then get details for a specific template
            details = templates_get_tag(template_name='custom_tag')

        Workflow:
            1. Use templates_list() to see all available templates
            2. Use templates_get_tag(template_name='NAME') to get specific requirements
            3. Use tags_create() with the template information to create the tag
        """
        return get_available_templates()

    @mcp.tool(annotations={"title": "Piwik PRO: Get Tag Template", "readOnlyHint": True})
    def templates_get_tag(template_name: str) -> dict:
        """Get detailed information about a specific Piwik PRO Tag Manager template.

        This tool provides comprehensive guidance on how to use tag templates with tags_create,
        including required attributes, examples, and best practices optimized for AI understanding.

        Args:
            template_name: Name of the template to get details for (e.g., 'custom_tag', 'piwik', 'google_analytics')

        Returns:
            Dictionary containing complete template information including:
            - Template description and use cases
            - Required and optional attributes with detailed explanations
            - Complete MCP tool usage examples
            - Best practices and common mistakes
            - Troubleshooting guide

        Examples:
            # Get detailed info for custom tag template
            custom_tag_info = templates_get_tag(template_name='custom_tag')

            # Get info for Piwik PRO analytics template
            piwik_info = templates_get_tag(template_name='piwik')

            # Get info for Google Analytics template
            ga_info = templates_get_tag(template_name='google_analytics')

        Workflow:
            1. Use piwik_get_available_templates() to see all available templates
            2. Use this tool to get specific requirements for your chosen template
            3. Use piwik_create_tag() with the template information to create the tag
        """
        return get_tag_template(template_name)

    @mcp.tool(annotations={"title": "Piwik PRO: List Trigger Templates", "readOnlyHint": True})
    def templates_list_triggers() -> dict:
        """List all available Piwik PRO Tag Manager trigger templates.

        This tool returns a list of all available trigger templates that can be used with triggers_create.
        Each template has detailed documentation available via templates_get_trigger.

        Returns:
            Dictionary containing:
            - available_templates: List of trigger template names
            - total_count: Number of available trigger templates
            - usage_guide: Instructions on how to use trigger templates
            - note: Information about trigger template documentation

        Examples:
            # Get list of all available trigger templates
            templates = templates_list_triggers()

            # Then get details for a specific trigger template
            details = templates_get_trigger(template_name='page_view')

        Workflow:
            1. Use templates_list_triggers() to see all available trigger templates
            2. Use templates_get_trigger(template_name='NAME') to get specific requirements
            3. Use triggers_create() with the template information to create the trigger
        """
        return get_available_trigger_templates()

    @mcp.tool(annotations={"title": "Piwik PRO: Get Trigger Template", "readOnlyHint": True})
    def templates_get_trigger(template_name: str) -> dict:
        """Get detailed information about a specific Piwik PRO Tag Manager trigger template.

        This tool provides comprehensive guidance on how to use trigger templates with triggers_create,
        including required attributes, examples, and best practices optimized for AI understanding.

        Args:
            template_name: Name of the trigger template to get details for
                (e.g., 'page_view', 'click', 'form_submission')

        Returns:
            Dictionary containing complete trigger template information including:
            - Template description and use cases
            - Required and optional attributes with detailed explanations
            - Complete MCP tool usage examples
            - Best practices and common mistakes
            - Troubleshooting guide

        Examples:
            # Get detailed info for page view trigger template
            page_view_info = templates_get_trigger(template_name='page_view')

            # Get info for click trigger template
            click_info = templates_get_trigger(template_name='click')

            # Get info for form submission trigger template
            form_info = templates_get_trigger(template_name='form_submission')

        Workflow:
            1. Use piwik_get_available_trigger_templates() to see all available trigger templates
            2. Use this tool to get specific requirements for your chosen trigger template
            3. Use piwik_create_trigger() with the template information to create the trigger
        """
        return get_trigger_template(template_name)

    @mcp.tool(annotations={"title": "Piwik PRO: List Variable Templates", "readOnlyHint": True})
    def templates_list_variables() -> dict:
        """List all available Piwik PRO Tag Manager variable templates.

        This tool provides discovery of all available variable templates that can be used with
        variables_create and variables_update operations. Each template includes comprehensive
        documentation with field mutability guidance for both create and update scenarios.

        Returns:
            Dictionary containing:
            - available_templates: List of template names (e.g., 'data_layer', 'custom_javascript')
            - total_count: Number of available templates
            - usage_guide: Workflow instructions for template discovery and usage
            - field_mutability: Overview of editable, create-only, and read-only fields

        Examples:
            # Get all available variable templates
            templates = templates_list_variables()

            # Example response structure:
            {
                "available_templates": ["data_layer", "custom_javascript", "constant"],
                "total_count": 3,
                "usage_guide": {
                    "discovery_workflow": [...],
                    "create_update_workflow": {...},
                    "field_mutability": {...}
                }
            }

        Workflow:
            1. Use this tool to see all available variable templates
            2. Use templates_get_variable() to get specific requirements and mutability info
            3. Use variables_create() or variables_update() with template information
        """
        return get_available_variable_templates()

    @mcp.tool(annotations={"title": "Piwik PRO: Get Variable Template", "readOnlyHint": True})
    def templates_get_variable(template_name: str) -> dict:
        """Get detailed information about a specific Piwik PRO Tag Manager variable template.

        This tool provides comprehensive guidance for using variable templates with both create_variable
        and update_variable operations. It includes complete field mutability information to help you
        understand which fields can be modified after creation.

        Args:
            template_name: Name of the variable template to get details for
                          Available templates include: 'data_layer', 'custom_javascript', 'constant'

        Returns:
            Dictionary containing complete variable template information including:
            - template_name and display_name
            - description and ai_usage_guide
            - mcp_usage: Separate guidance for create_variable and update_variable
            - required_attributes, optional_attributes, read_only_attributes
            - field_mutability_guide: Detailed explanation of field editability
            - complete_examples: Working examples for both create and update operations
            - troubleshooting and best practices

        Examples:
            # Get dataLayer variable template info
            template = templates_get_variable(template_name='data_layer')

            # Get custom JavaScript variable template info
            template = templates_get_variable(template_name='custom_javascript')

        Field Mutability Overview:
            ✅ Editable: name, is_active, template-specific options (can be updated anytime)
            ⚠️ Create-only: variable_type (set during creation, immutable after)
            🚫 Read-only: created_at, updated_at (auto-generated, never user-modifiable)

        Workflow:
            1. Use templates_list_variables() to see all available templates
            2. Use this tool to get specific requirements and mutability info for your chosen template
            3. Use variables_create() with the template information to create variables
            4. Use variables_update() with editable fields only to update variables
        """
        return get_variable_template(template_name)
