"""Tests for Analytics Goals MCP tools."""

from unittest.mock import Mock, patch

import pytest


class TestGoalsCrudFunctional:
    @pytest.fixture
    def mock_piwik_client(self):
        with patch("piwik_pro_mcp.tools.analytics.goals.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance

            # Create
            mock_instance.analytics.create_goal.return_value = Mock(
                model_dump=lambda: {
                    "data": {
                        "id": "goal-1",
                        "type": "Goal",
                        "attributes": {
                            "website_id": "app-1",
                            "name": "Test Goal",
                            "description": "Test description",
                            "trigger": "url",
                            "pattern_type": "contains",
                            "pattern": "/checkout",
                            "allow_multiple": False,
                            "case_sensitive": False,
                            "revenue": "10.00",
                        },
                    }
                }
            )

            # List
            mock_instance.analytics.list_goals.return_value = Mock(
                model_dump=lambda: {
                    "data": [
                        {
                            "id": "goal-1",
                            "type": "Goal",
                            "attributes": {
                                "website_id": "app-1",
                                "name": "Test Goal",
                                "description": "Test description",
                                "trigger": "url",
                                "pattern_type": "contains",
                                "pattern": "/checkout",
                                "allow_multiple": False,
                                "case_sensitive": False,
                                "revenue": "10.00",
                            },
                        },
                        {
                            "id": "goal-2",
                            "type": "Goal",
                            "attributes": {
                                "website_id": "app-1",
                                "name": "Another Goal",
                                "description": None,
                                "trigger": "manually",
                                "pattern_type": None,
                                "pattern": None,
                                "allow_multiple": False,
                                "case_sensitive": False,
                                "revenue": "0",
                            },
                        },
                    ],
                    "meta": {"total": 2},
                }
            )

            # Get
            mock_instance.analytics.get_goal.return_value = Mock(
                model_dump=lambda: {
                    "data": {
                        "id": "goal-1",
                        "type": "Goal",
                        "attributes": {
                            "website_id": "app-1",
                            "name": "Test Goal",
                            "description": "Test description",
                            "trigger": "url",
                            "pattern_type": "contains",
                            "pattern": "/checkout",
                            "allow_multiple": False,
                            "case_sensitive": False,
                            "revenue": "10.00",
                        },
                    }
                }
            )

            # Update
            mock_instance.analytics.update_goal.return_value = Mock(
                model_dump=lambda: {
                    "data": {
                        "id": "goal-1",
                        "type": "Goal",
                        "attributes": {
                            "website_id": "app-1",
                            "name": "Updated Goal",
                            "description": "Updated description",
                            "trigger": "url",
                            "pattern_type": "exact",
                            "pattern": "/success",
                            "allow_multiple": True,
                            "case_sensitive": True,
                            "revenue": "25.50",
                        },
                    }
                }
            )

            # Delete returns None (204)
            mock_instance.analytics.delete_goal.return_value = None

            yield mock_instance

    @pytest.mark.asyncio
    async def test_goals_create_functional(self, mcp_server, mock_piwik_client):
        result = await mcp_server.call_tool(
            "analytics_goals_create",
            {
                "website_id": "app-1",
                "name": "Test Goal",
                "trigger": "url",
                "revenue": "10.00",
                "description": "Test description",
                "pattern_type": "contains",
                "pattern": "/checkout",
                "allow_multiple": False,
                "case_sensitive": False,
            },
        )

        assert isinstance(result, tuple) and len(result) == 2
        _, data = result
        assert data["data"]["id"] == "goal-1"
        assert data["data"]["attributes"]["name"] == "Test Goal"
        mock_piwik_client.analytics.create_goal.assert_called_once()

    @pytest.mark.asyncio
    async def test_goals_create_minimal_manual_trigger(self, mcp_server, mock_piwik_client):
        """Test creating a goal with manual trigger (no pattern required)."""
        result = await mcp_server.call_tool(
            "analytics_goals_create",
            {
                "website_id": "app-1",
                "name": "Manual Goal",
                "trigger": "manually",
                "revenue": "0",
            },
        )

        assert isinstance(result, tuple) and len(result) == 2
        _, data = result
        assert data["data"]["id"] == "goal-1"

    @pytest.mark.asyncio
    async def test_goals_list_functional(self, mcp_server, mock_piwik_client):
        result = await mcp_server.call_tool(
            "analytics_goals_list",
            {"website_id": "app-1", "limit": 10, "offset": 0},
        )

        assert isinstance(result, tuple) and len(result) == 2
        _, data = result
        assert isinstance(data["data"], list)
        assert len(data["data"]) == 2
        assert data["meta"]["total"] == 2
        mock_piwik_client.analytics.list_goals.assert_called_once_with(website_id="app-1", limit=10, offset=0)

    @pytest.mark.asyncio
    async def test_goals_get_functional(self, mcp_server, mock_piwik_client):
        result = await mcp_server.call_tool(
            "analytics_goals_get",
            {"goal_id": "goal-1", "website_id": "app-1"},
        )

        assert isinstance(result, tuple) and len(result) == 2
        _, data = result
        assert data["data"]["id"] == "goal-1"
        assert data["data"]["attributes"]["name"] == "Test Goal"
        mock_piwik_client.analytics.get_goal.assert_called_once_with(goal_id="goal-1", website_id="app-1")

    @pytest.mark.asyncio
    async def test_goals_update_functional(self, mcp_server, mock_piwik_client):
        result = await mcp_server.call_tool(
            "analytics_goals_update",
            {
                "goal_id": "goal-1",
                "website_id": "app-1",
                "name": "Updated Goal",
                "trigger": "url",
                "revenue": "25.50",
                "description": "Updated description",
                "pattern_type": "exact",
                "pattern": "/success",
                "allow_multiple": True,
                "case_sensitive": True,
            },
        )

        assert isinstance(result, tuple) and len(result) == 2
        _, data = result
        assert data["data"]["id"] == "goal-1"
        assert data["data"]["attributes"]["name"] == "Updated Goal"
        assert data["data"]["attributes"]["revenue"] == "25.50"
        mock_piwik_client.analytics.update_goal.assert_called_once()

    @pytest.mark.asyncio
    async def test_goals_delete_functional(self, mcp_server, mock_piwik_client):
        result = await mcp_server.call_tool(
            "analytics_goals_delete",
            {"goal_id": "goal-1", "website_id": "app-1"},
        )

        assert isinstance(result, tuple) and len(result) == 2
        _, data = result
        # Verify OperationStatusResponse structure
        assert data["status"] == "success"
        assert data["message"] == "Goal goal-1 deleted successfully"
        mock_piwik_client.analytics.delete_goal.assert_called_once_with(goal_id="goal-1", website_id="app-1")
