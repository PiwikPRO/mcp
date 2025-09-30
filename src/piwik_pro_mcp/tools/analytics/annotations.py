"""
Analytics user annotations tools.
"""

from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from ...common import create_piwik_client


def register_analytics_tools(mcp: FastMCP) -> None:
    """Register Analytics user annotation tools with the MCP server."""

    @mcp.tool(annotations={"title": "Piwik PRO: Create User Annotation"})
    def analytics_annotations_create(
        website_id: str,
        content: str,
        date: str,
        visibility: str = "private",
    ) -> Dict[str, Any]:
        """
        Create a user annotation.

        Args:
            website_id: Website UUID
            content: Annotation content (max 150 chars)
            date: Date in YYYY-MM-DD format
            visibility: "private" (default) or "public"

        Returns:
            Created annotation resource as a dict
        """
        client = create_piwik_client()
        return client.analytics.create_user_annotation(
            website_id=website_id, content=content, date=date, visibility=visibility
        )

    @mcp.tool(annotations={"title": "Piwik PRO: List User Annotations", "readOnlyHint": True})
    def analytics_annotations_list(
        website_id: str,
        date_from: Optional[List[str]] = None,
        date_to: Optional[List[str]] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        List user annotations for a website.

        Args:
            website_id: Website UUID
            date_from: Optional list of start dates (YYYY-MM-DD)
            date_to: Optional list of end dates (YYYY-MM-DD)
            limit: Max number of items
            offset: Number of items to skip

        Returns:
            Annotations list and metadata
        """
        client = create_piwik_client()

        # If both date_from and date_to provided, ensure lengths match
        if date_from is not None and date_to is not None and len(date_from) != len(date_to):
            raise RuntimeError("date_from and date_to must have the same number of items")

        return client.analytics.list_user_annotations(
            website_id=website_id, date_from=date_from, date_to=date_to, limit=limit, offset=offset
        )

    @mcp.tool(annotations={"title": "Piwik PRO: Get User Annotation", "readOnlyHint": True})
    def analytics_annotations_get(annotation_id: str, website_id: str) -> Dict[str, Any]:
        """
        Get a user annotation by ID.
        """
        client = create_piwik_client()
        return client.analytics.get_user_annotation(annotation_id=annotation_id, website_id=website_id)

    @mcp.tool(annotations={"title": "Piwik PRO: Delete User Annotation"})
    def analytics_annotations_delete(annotation_id: str, website_id: str) -> None:
        """
        Delete a user annotation by ID.
        """
        client = create_piwik_client()
        client.analytics.delete_user_annotation(annotation_id=annotation_id, website_id=website_id)

    @mcp.tool(annotations={"title": "Piwik PRO: Update User Annotation"})
    def analytics_annotations_update(
        annotation_id: str,
        website_id: str,
        content: str,
        date: str,
        visibility: str = "private",
    ) -> Dict[str, Any]:
        """
        Update an existing user annotation.

        Args:
            annotation_id: Annotation UUID
            website_id: Website UUID
            content: Updated content (max 150 chars)
            date: Updated date in YYYY-MM-DD format
            visibility: "private" (default) or "public"

        Returns:
            Updated annotation resource as a dict
        """
        client = create_piwik_client()
        return client.analytics.update_user_annotation(
            annotation_id=annotation_id,
            website_id=website_id,
            content=content,
            date=date,
            visibility=visibility,
        )






