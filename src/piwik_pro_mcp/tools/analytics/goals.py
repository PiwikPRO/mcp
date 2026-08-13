"""
Analytics goals tools.
"""

from mcp.server.fastmcp import FastMCP

from ...common import create_piwik_client
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
        description: str | None = None,
        pattern_type: str | None = None,
        pattern: str | None = None,
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

        Use this before goal conversion queries when the user names a specific goal.
        Match the goal by exact name in `data[].attributes.name`, then use the goal's
        `id` as the `goal_uuid` filter value in `analytics_query_execute`. Do not put
        `goal_uuid` in query columns when filtering to a single goal.

        Args:
            website_id: Website/App UUID
            limit: Maximum number of rows to return (default: 10, min: 1, max: 100000)
            offset: Number of rows to skip (default: 0, min: 0)

        Returns:
            Goals list with metadata. Each goal has `id` (UUID) and `attributes.name`.
        """
        client = create_piwik_client()
        api_resp = client.analytics.list_goals(
            website_id=website_id,
            limit=limit,
            offset=offset,
        )
        goals_list = GoalsList(**api_resp.model_dump())
        goals_list.meta["query_planning_hint"] = (
            "For conversions of one named goal: use that goal's `id` in "
            "analytics_query_execute `filters` as "
            '{"column_id": "goal_uuid", "condition": {"operator": "eq", "value": "<goal-id>"}}. '
            "Do not add `goal_uuid` to `columns`. Group by timestamp with "
            'transformation_id "to_date", select metric `goal_conversions`, and set '
            "`order_by` to the goal_conversions column index with direction `desc`."
        )
        return goals_list

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
        description: str | None = None,
        pattern_type: str | None = None,
        pattern: str | None = None,
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
