"""
Version management tools for Piwik PRO Tag Manager.

This module provides MCP tools for managing Tag Manager versions,
including listing, getting draft/published versions, and publishing.
"""

from mcp.server.fastmcp import FastMCP

from piwik_pro_mcp.api.exceptions import BadRequestError, NotFoundError
from piwik_pro_mcp.api.methods.tag_manager.models import TagManagerListResponse, TagManagerSingleResponse

from ...common.utils import create_piwik_client
from .models import PublishStatusResponse


def list_versions(
    app_id: str,
    limit: int = 10,
    offset: int = 0,
) -> TagManagerListResponse:
    try:
        client = create_piwik_client()
        response = client.tag_manager.list_versions(app_id=app_id, limit=limit, offset=offset)
        return TagManagerListResponse(**response)
    except Exception as e:
        raise RuntimeError(f"Failed to list versions: {str(e)}")


def get_draft_version(app_id: str) -> TagManagerSingleResponse:
    try:
        client = create_piwik_client()
        response = client.tag_manager.get_draft_version(app_id)
        return TagManagerSingleResponse(**response)
    except NotFoundError:
        raise RuntimeError(f"Draft version not found for app {app_id}")
    except Exception as e:
        raise RuntimeError(f"Failed to get draft version: {str(e)}")


def get_published_version(app_id: str) -> TagManagerSingleResponse:
    try:
        client = create_piwik_client()
        response = client.tag_manager.get_published_version(app_id)
        return TagManagerSingleResponse(**response)
    except NotFoundError:
        raise RuntimeError(f"Published version not found for app {app_id}")
    except Exception as e:
        raise RuntimeError(f"Failed to get published version: {str(e)}")


def publish_draft_version(app_id: str) -> PublishStatusResponse:
    try:
        client = create_piwik_client()
        response = client.tag_manager.publish_draft_version(app_id)

        # Handle successful response
        # For async operations (202), response contains version and operation info
        # For sync operations (204), response is None
        if response and isinstance(response, dict):
            # Extract operation info for async publish operations
            operation_id = None
            version_id = None

            if "data" in response:
                version_id = response["data"].get("id")
                if "relationships" in response["data"] and "operation" in response["data"]["relationships"]:
                    operation_data = response["data"]["relationships"]["operation"].get("data", {})
                    operation_id = operation_data.get("id")

            message = "Draft version publish initiated"
            if operation_id:
                message += f" (Operation ID: {operation_id})"

            return PublishStatusResponse(
                status="success",
                message=message,
                version_info={
                    "version_id": version_id,
                    "operation_id": operation_id,
                    "is_async": True,
                    "full_response": response,
                },
            )
        else:
            # Handle sync operations (204 No Content)
            return PublishStatusResponse(
                status="success",
                message="Draft version published successfully",
                version_info={"is_async": False},
            )
    except BadRequestError as e:
        raise RuntimeError(f"Failed to publish draft version: {e.message}")
    except Exception as e:
        raise RuntimeError(f"Failed to publish draft version: {str(e)}")


def register_version_tools(mcp: FastMCP) -> None:
    """Register all version management tools with the MCP server."""

    @mcp.tool(annotations={"title": "Piwik PRO: List Versions", "readOnlyHint": True})
    def versions_list(
        app_id: str,
        limit: int = 10,
        offset: int = 0,
    ) -> TagManagerListResponse:
        """List versions for an app in Piwik PRO Tag Manager.

        Args:
            app_id: UUID of the app
            limit: Maximum number of versions to return (default: 10)
            offset: Number of versions to skip (default: 0)

        Returns:
            Dictionary containing version list and metadata including:
            - data: List of version objects with id, name, version_type, and timestamps
            - meta: Metadata with pagination information
        """
        return list_versions(app_id=app_id, limit=limit, offset=offset)

    @mcp.tool(annotations={"title": "Piwik PRO: Get Draft Version", "readOnlyHint": True})
    def versions_get_draft(app_id: str) -> TagManagerSingleResponse:
        """Get draft version for an app.

        Args:
            app_id: UUID of the app

        Returns:
            Dictionary containing draft version details including:
            - data: Draft version object with all tags, triggers, variables
            - Version configuration and metadata
        """
        return get_draft_version(app_id)

    @mcp.tool(annotations={"title": "Piwik PRO: Get Published Version", "readOnlyHint": True})
    def versions_get_published(app_id: str) -> TagManagerSingleResponse:
        """Get published version for an app.

        Args:
            app_id: UUID of the app

        Returns:
            Dictionary containing published version details including:
            - data: Published version object with all active tags, triggers, variables
            - Version configuration and metadata
        """
        return get_published_version(app_id)

    @mcp.tool(annotations={"title": "Piwik PRO: Publish Draft Version"})
    def versions_publish_draft(app_id: str) -> PublishStatusResponse:
        """Publish the draft version to make it live.

        This will make all tags, triggers, and variables in the draft version
        active on your website.

        Args:
            app_id: UUID of the app

        Returns:
            Dictionary containing operation response including:
            - Operation status and details
            - Information about the published version
        """
        return publish_draft_version(app_id)
