"""Tests for Analytics Annotations MCP tools."""

from unittest.mock import Mock, patch

import pytest

from piwik_pro_mcp.api.methods.analytics.models import (
    SystemAnnotationAttributes,
    SystemAnnotationResource,
    UserAnnotationAttributes,
    UserAnnotationResource,
)


class TestAnnotationsCrudFunctional:
    @pytest.fixture
    def mock_piwik_client(self):
        with patch("piwik_pro_mcp.tools.analytics.annotations.create_piwik_client") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance

            # Create
            mock_instance.analytics.create_user_annotation.return_value = Mock(
                model_dump=lambda: {
                    "data": {
                        "id": "ann-1",
                        "type": "UserAnnotation",
                        "attributes": {
                            "date": "2025-09-01",
                            "content": "Created",
                            "visibility": "private",
                            "website_id": "app-1",
                            "is_author": True,
                        },
                    }
                }
            )

            user_list = Mock()
            user_list.data = [
                UserAnnotationResource(
                    id="ann-2",
                    type="UserAnnotation",
                    attributes=UserAnnotationAttributes(
                        date="2025-09-02", content="User A", visibility="private", website_id="app-1"
                    ),
                )
            ]
            system_list = Mock()
            system_list.data = [
                SystemAnnotationResource(
                    id="ann-3",
                    type="SystemAnnotation",
                    attributes=SystemAnnotationAttributes(date="2025-09-03", content="System A"),
                )
            ]
            mock_instance.analytics.list_user_annotations.return_value = user_list
            mock_instance.analytics.list_system_annotations.return_value = system_list

            # Get
            mock_instance.analytics.get_user_annotation.return_value = Mock(
                model_dump=lambda: {
                    "data": {
                        "id": "ann-2",
                        "type": "UserAnnotation",
                        "attributes": {"date": "2025-09-02", "content": "User A"},
                    }
                }
            )

            # Update
            mock_instance.analytics.update_user_annotation.return_value = Mock(
                model_dump=lambda: {
                    "data": {
                        "id": "ann-2",
                        "type": "UserAnnotation",
                        "attributes": {"date": "2025-09-04", "content": "Updated"},
                    }
                }
            )

            # Delete returns None (204)
            mock_instance.analytics.delete_user_annotation.return_value = None

            yield mock_instance

    @pytest.mark.asyncio
    async def test_annotations_create_functional(self, mcp_server, mock_piwik_client):
        result = await mcp_server.call_tool(
            "analytics_annotations_create",
            {"app_id": "app-1", "content": "Created", "date": "2025-09-01", "visibility": "private"},
        )

        assert isinstance(result, tuple) and len(result) == 2
        _, data = result
        assert data["data"]["id"] == "ann-1"
        mock_piwik_client.analytics.create_user_annotation.assert_called_once()

    @pytest.mark.asyncio
    async def test_annotations_list_functional_single_dates_wrapped(self, mcp_server, mock_piwik_client):
        result = await mcp_server.call_tool(
            "analytics_annotations_list",
            {"app_id": "app-1", "date_from": "2025-09-01", "date_to": "2025-09-30", "source": "all"},
        )

        assert isinstance(result, tuple) and len(result) == 2
        _, data = result
        assert isinstance(data["data"], list)
        assert data["meta"]["total"] == 2

        # Verify client was called with lists for date params
        user_call = mock_piwik_client.analytics.list_user_annotations.call_args
        sys_call = mock_piwik_client.analytics.list_system_annotations.call_args
        assert user_call[1]["date_from"] == ["2025-09-01"]
        assert user_call[1]["date_to"] == ["2025-09-30"]
        assert sys_call[1]["date_from"] == ["2025-09-01"]
        assert sys_call[1]["date_to"] == ["2025-09-30"]

    @pytest.mark.asyncio
    async def test_annotations_get_functional(self, mcp_server, mock_piwik_client):
        result = await mcp_server.call_tool(
            "analytics_annotations_get",
            {"annotation_id": "ann-2", "app_id": "app-1"},
        )

        assert isinstance(result, tuple) and len(result) == 2
        _, data = result
        assert data["data"]["id"] == "ann-2"
        mock_piwik_client.analytics.get_user_annotation.assert_called_once_with(annotation_id="ann-2", app_id="app-1")

    @pytest.mark.asyncio
    async def test_annotations_update_functional(self, mcp_server, mock_piwik_client):
        result = await mcp_server.call_tool(
            "analytics_annotations_update",
            {
                "annotation_id": "ann-2",
                "app_id": "app-1",
                "content": "Updated",
                "date": "2025-09-04",
                "visibility": "public",
            },
        )

        assert isinstance(result, tuple) and len(result) == 2
        _, data = result
        assert data["data"]["id"] == "ann-2"
        mock_piwik_client.analytics.update_user_annotation.assert_called_once()

    @pytest.mark.asyncio
    async def test_annotations_delete_functional(self, mcp_server, mock_piwik_client):
        # Ensure delete path is exercised and returns OperationStatusResponse
        result = await mcp_server.call_tool(
            "analytics_annotations_delete",
            {"annotation_id": "ann-2", "app_id": "app-1"},
        )

        assert isinstance(result, tuple) and len(result) == 2
        _, data = result
        # Verify OperationStatusResponse structure
        assert data["status"] == "success"
        assert data["message"] == "Annotation ann-2 deleted successfully"
        mock_piwik_client.analytics.delete_user_annotation.assert_called_once_with(
            annotation_id="ann-2", app_id="app-1"
        )
