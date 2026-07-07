"""
Operation management tools for Piwik PRO Tag Manager.

This module provides MCP tools for retrieving Tag Manager async operation status.
"""

from mcp.server.fastmcp import FastMCP

from piwik_pro_mcp.api.exceptions import NotFoundError
from piwik_pro_mcp.api.methods.tag_manager.models import TagManagerSingleResponse

from ...common.utils import create_piwik_client


def get_operation(app_id: str, operation_id: str) -> TagManagerSingleResponse:
    try:
        client = create_piwik_client()
        response = client.tag_manager.get_operation(app_id, operation_id)
        if not isinstance(response, dict):
            raise RuntimeError(f"Unexpected response type from get_operation: {type(response).__name__}")
        return TagManagerSingleResponse(**response)
    except NotFoundError:
        raise RuntimeError(f"Operation with ID {operation_id} not found in app {app_id}")
    except Exception as e:
        raise RuntimeError(f"Failed to get operation: {str(e)}")


def register_operation_tools(mcp: FastMCP) -> None:
    """Register all operation management tools with the MCP server."""

    @mcp.tool(annotations={"title": "Piwik PRO: Get Operation", "readOnlyHint": True})
    def operations_get(app_id: str, operation_id: str) -> TagManagerSingleResponse:
        """Get a Tag Manager async operation by ID.

        Use this tool to check the status of background operations started by
        publish, restore, snapshot, copy, export, import, and similar Tag Manager actions.

        Args:
            app_id: UUID of the app
            operation_id: UUID of the operation

        Returns:
            Dictionary containing operation details including:
            - data.id: Operation UUID
            - data.type: Always ``operation``
            - data.attributes.operation_type: Operation kind (e.g. ``publish``,
              ``create_snapshot``, ``import/version``)
            - data.attributes.state: Lifecycle state (``created``, ``started``,
              ``completed``, or ``failed``)
            - data.attributes.parameters: Input parameters for the operation;
              shape depends on ``operation_type`` (e.g. ``target_app_id`` and
              ``source_version_id`` for ``import/version``)
            - data.attributes.summary: Result summary when available; may
              contain ``tags``, ``triggers``, and ``variables`` lists. Each
              entry maps source and target resource IDs/names and includes
              ``is_renamed`` when a name changed during import or copy.
              When working with versions it can contain following fields:
              ``export_file_id``, ``version_id``, ``version_type``,
              ``version_major``, ``version_minor``, ``change_type``.
            - data.attributes.created_at: When the operation was created
            - data.attributes.started_at: When processing started (if started)
            - data.attributes.completed_at: When the operation finished
              successfully (if completed)
            - data.attributes.failed_at: When the operation failed (if failed)
            - data.attributes.updated_at: Last update timestamp
        """
        return get_operation(app_id, operation_id)
