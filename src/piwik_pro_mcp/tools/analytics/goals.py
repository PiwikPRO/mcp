"""
Analytics goals tools.
"""

from typing import Optional

from mcp.server.fastmcp import FastMCP

from ...common import create_piwik_client
from ...responses import OperationStatusResponse
from .models import (
    GoalItem,
    GoalsList,
)


def register_goals_tools(mcp: FastMCP) -> None:
    """Register Analytics goals tools with the MCP server."""

    @mcp.tool(annotations={"title": "Piwik PRO: Create Goal"})
    def analytics_goals_create(
        website_id: str,
        name: str,
        trigger: str,
        revenue: str,
        description: Optional[str] = None,
        pattern_type: Optional[str] = None,
        pattern: Optional[str] = None,
        allow_multiple: bool = False,
        case_sensitive: bool = False,
    ) -> GoalItem:
        """
        Create a new goal for a website.

        Args:
            website_id: Website/App UUID
            name: Name of the goal
            trigger: Trigger type. Valid values: "url", "title", "event_name",
                    "event_category", "event_action", "file", "external_website", "manually"
            revenue: Goal revenue value as string in monetary format (e.g., "10.22" or "0")
            description: Optional description of the goal (max 1024 chars)
            pattern_type: Condition operator for pattern matching. Valid values: "contains",
                         "exact", "regex". Required for all triggers except "manually"
            pattern: Condition value to match against. Required for all triggers except "manually"
            allow_multiple: Whether the goal can be converted more than once per visit (default: False)
            case_sensitive: Whether pattern matching is case sensitive (default: False)

        Returns:
            Created goal resource
        """
        client = create_piwik_client()
        api_resp = client.analytics.create_goal(
            website_id=website_id,
            name=name,
            trigger=trigger,
            revenue=revenue,
            description=description,
            pattern_type=pattern_type,
            pattern=pattern,
            allow_multiple=allow_multiple,
            case_sensitive=case_sensitive,
        )
        return GoalItem(**api_resp.model_dump())

    @mcp.tool(annotations={"title": "Piwik PRO: List Goals", "readOnlyHint": True})
    def analytics_goals_list(
        website_id: str,
        limit: int = 10,
        offset: int = 0,
    ) -> GoalsList:
        """
        List all goals for a website.

        Args:
            website_id: Website/App UUID
            limit: Maximum number of rows to return (default: 10, min: 1, max: 100000)
            offset: Number of rows to skip (default: 0, min: 0)

        Returns:
            Goals list with metadata
        """
        client = create_piwik_client()
        api_resp = client.analytics.list_goals(
            website_id=website_id,
            limit=limit,
            offset=offset,
        )
        return GoalsList(**api_resp.model_dump())

    @mcp.tool(annotations={"title": "Piwik PRO: Get Goal", "readOnlyHint": True})
    def analytics_goals_get(goal_id: str, website_id: str) -> GoalItem:
        """
        Get a specific goal by ID.

        Args:
            goal_id: Goal UUID
            website_id: Website/App UUID

        Returns:
            Goal resource
        """
        client = create_piwik_client()
        api_resp = client.analytics.get_goal(goal_id=goal_id, website_id=website_id)
        return GoalItem(**api_resp.model_dump())

    @mcp.tool(annotations={"title": "Piwik PRO: Update Goal"})
    def analytics_goals_update(
        goal_id: str,
        website_id: str,
        name: str,
        trigger: str,
        revenue: str,
        description: Optional[str] = None,
        pattern_type: Optional[str] = None,
        pattern: Optional[str] = None,
        allow_multiple: bool = False,
        case_sensitive: bool = False,
    ) -> GoalItem:
        """
        Update an existing goal. Required fields: name, trigger, revenue, website_id.

        Args:
            goal_id: Goal UUID
            website_id: Website/App UUID
            name: Name of the goal
            trigger: Trigger type. Valid values: "url", "title", "event_name",
                    "event_category", "event_action", "file", "external_website", "manually"
            revenue: Goal revenue value as string in monetary format (e.g., "10.22" or "0")
            description: Optional description of the goal (max 1024 chars)
            pattern_type: Condition operator for pattern matching. Valid values: "contains",
                         "exact", "regex". Required for all triggers except "manually"
            pattern: Condition value to match against. Required for all triggers except "manually"
            allow_multiple: Whether the goal can be converted more than once per visit (default: False)
            case_sensitive: Whether pattern matching is case sensitive (default: False)

        Returns:
            Updated goal resource
        """
        client = create_piwik_client()
        api_resp = client.analytics.update_goal(
            goal_id=goal_id,
            website_id=website_id,
            name=name,
            trigger=trigger,
            revenue=revenue,
            description=description,
            pattern_type=pattern_type,
            pattern=pattern,
            allow_multiple=allow_multiple,
            case_sensitive=case_sensitive,
        )
        return GoalItem(**api_resp.model_dump())

    @mcp.tool(annotations={"title": "Piwik PRO: Delete Goal"})
    def analytics_goals_delete(goal_id: str, website_id: str) -> OperationStatusResponse:
        """
        Delete a goal by ID.

        Args:
            goal_id: Goal UUID
            website_id: Website/App UUID

        Returns:
            Operation status with success message
        """
        try:
            client = create_piwik_client()
            client.analytics.delete_goal(goal_id=goal_id, website_id=website_id)
            return OperationStatusResponse(
                status="success",
                message=f"Goal {goal_id} deleted successfully",
            )
        except Exception as e:
            raise RuntimeError(f"Failed to delete goal: {str(e)}")
