"""
Analytics user annotations tools.
"""

from typing import Optional

from mcp.server.fastmcp import FastMCP

from ...common import create_piwik_client
from ...responses import OperationStatusResponse
from .models import (
    AnnotationItem,
    AnnotationsList,
)


def register_annotations_tools(mcp: FastMCP) -> None:  # noqa: PLR0915
    """Register Analytics user annotation tools with the MCP server."""

    @mcp.tool(annotations={"title": "Piwik PRO: Create Annotation"})
    def analytics_annotations_create(
        app_id: str,
        content: str,
        date: str,
        visibility: str = "private",
    ) -> AnnotationItem:
        """
        Create a user annotation.

        Args:
            app_id: App UUID
            content: Annotation content (max 150 chars)
            date: Date in YYYY-MM-DD format
            visibility: "private" (default) or "public"

        Returns:
            Created annotation resource as a dict
        """
        client = create_piwik_client()
        api_resp = client.analytics.create_user_annotation(
            app_id=app_id,
            content=content,
            date=date,
            visibility=visibility,
        )
        return AnnotationItem(**api_resp.model_dump())

    @mcp.tool(annotations={"title": "Piwik PRO: List Annotations", "readOnlyHint": True})
    def analytics_annotations_list(
        app_id: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        source: str = "all",
        limit: int = 10,
        offset: int = 0,
    ) -> AnnotationsList:
        """
        List user annotations for an app.

        Args:
            app_id: App UUID
            date_from: Optional start date (YYYY-MM-DD)
            date_to: Optional end date (YYYY-MM-DD)
            limit: Max number of items
            offset: Number of items to skip

        Returns:
            Annotations list and metadata
        """
        client = create_piwik_client()

        # API expects lists for repeated query params; wrap single dates if provided
        date_from_list = [date_from] if date_from else None
        date_to_list = [date_to] if date_to else None

        # Fetch annotations by source selection
        user_resp = None
        system_resp = None

        src = (source or "all").lower()
        if src in ("all", "user"):
            user_resp = client.analytics.list_user_annotations(
                app_id=app_id, date_from=date_from_list, date_to=date_to_list, limit=limit, offset=offset
            )
        if src in ("all", "system"):
            system_resp = client.analytics.list_system_annotations(
                date_from=date_from_list, date_to=date_to_list, limit=limit, offset=offset
            )
        combined = user_resp.data + system_resp.data
        combined.sort(key=lambda x: x.attributes.date)
        # Compose meta: we won't perfectly normalize counts across sources; provide total
        total = 0
        total += len(user_resp.data)
        total += len(system_resp.data)

        return AnnotationsList(data=combined, meta={"total": total})

    @mcp.tool(annotations={"title": "Piwik PRO: Get Annotation", "readOnlyHint": True})
    def analytics_annotations_get(annotation_id: str, app_id: str) -> AnnotationItem:
        """
        Get a user annotation by ID.
        """
        client = create_piwik_client()
        api_resp = client.analytics.get_user_annotation(annotation_id=annotation_id, app_id=app_id)
        return AnnotationItem(**api_resp.model_dump())

    @mcp.tool(annotations={"title": "Piwik PRO: Delete Annotation"})
    def analytics_annotations_delete(annotation_id: str, app_id: str) -> OperationStatusResponse:
        """
        Delete a user annotation by ID.

        Args:
            annotation_id: Annotation UUID
            app_id: App UUID

        Returns:
            Operation status with success message
        """
        try:
            client = create_piwik_client()
            # Check type before attempting delete (can't delete system via user endpoint)
            details = client.analytics.get_user_annotation(annotation_id=annotation_id, app_id=app_id)
            item_type = None
            if details is not None:
                # Support both Pydantic response objects and plain dicts
                if hasattr(details, "data"):
                    try:
                        item_type = getattr(details.data, "type", None)
                    except Exception:
                        item_type = None
                elif isinstance(details, dict):
                    item_type = details.get("data", {}).get("type")
            if item_type and item_type.lower() == "systemannotation":
                raise RuntimeError("System annotations cannot be deleted.")
            client.analytics.delete_user_annotation(annotation_id=annotation_id, app_id=app_id)
            return OperationStatusResponse(
                status="success",
                message=f"Annotation {annotation_id} deleted successfully",
            )
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to delete annotation: {str(e)}")

    @mcp.tool(annotations={"title": "Piwik PRO: Update Annotation"})
    def analytics_annotations_update(
        annotation_id: str,
        app_id: str,
        content: str,
        date: str,
        visibility: str = "private",
    ) -> AnnotationItem:
        """
        Update an existing user annotation.

        Args:
            annotation_id: Annotation UUID
            app_id: App UUID
            content: Updated content (max 150 chars)
            date: Updated date in YYYY-MM-DD format
            visibility: "private" (default) or "public"

        Returns:
            Updated annotation resource as a dict
        """
        client = create_piwik_client()
        api_resp = client.analytics.update_user_annotation(
            annotation_id=annotation_id,
            app_id=app_id,
            content=content,
            date=date,
            visibility=visibility,
        )
        return AnnotationItem(**api_resp.model_dump())
