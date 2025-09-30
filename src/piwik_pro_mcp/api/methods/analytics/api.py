"""
Analytics API for Piwik PRO - User Annotations.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from piwik_pro_mcp.api.methods.analytics.models import (
    SystemAnnotationListResponse,
    UserAnnotationListResponse,
    UserAnnotationSingleResponse,
)

if TYPE_CHECKING:
    from ...client import PiwikProClient


class AnalyticsAPI:
    """Analytics API client for Piwik PRO (annotations)."""

    def __init__(self, client: "PiwikProClient"):
        """
        Initialize Analytics API client.

        Args:
            client: Piwik PRO HTTP client instance
        """
        self.client = client

    # Base endpoint
    _USER_ANNOTATIONS_BASE = "/api/analytics/v1/manage/annotation/user"
    _SYSTEM_ANNOTATIONS_BASE = "/api/analytics/v1/manage/annotation/system"

    def create_user_annotation(
        self,
        app_id: str,
        content: str,
        date: str,
        visibility: Optional[str] = "private",
    ) -> UserAnnotationSingleResponse:
        """
        Create a new user annotation.

        Args:
            app_id: App UUID (sent as website_id in API payload)
            content: Annotation content (max 150 chars)
            date: Annotation date (YYYY-MM-DD)
            visibility: "private" (default) or "public"

        Returns:
            Dictionary with created annotation
        """
        attributes: Dict[str, Any] = {
            "website_id": app_id,
            "content": content,
            "date": date,
        }
        if visibility is not None:
            attributes["visibility"] = visibility

        data = {"data": {"type": "UserAnnotation", "attributes": attributes}}
        response = self.client.post(f"{self._USER_ANNOTATIONS_BASE}/", data=data)
        return UserAnnotationSingleResponse(**(response or {}))

    # No generic alias for create (user-only)

    def list_user_annotations(
        self,
        app_id: str,
        date_from: Optional[List[str]] = None,
        date_to: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> UserAnnotationListResponse:
        """
        List user annotations for a website with optional date ranges.

        Args:
            app_id: App UUID (required; sent as website_id query param)
            date_from: Optional list of start dates (YYYY-MM-DD)
            date_to: Optional list of end dates (YYYY-MM-DD)
            limit: Max number of items
            offset: Number of items to skip

        Returns:
            Dictionary with annotations list and meta
        """
        params: Dict[str, Any] = {"website_id": app_id}

        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset

        # Repeated query params: requests will encode lists as repeated keys
        if date_from is not None:
            params["date_from"] = date_from
        if date_to is not None:
            params["date_to"] = date_to

        response = self.client.get(f"{self._USER_ANNOTATIONS_BASE}/", params=params)
        return UserAnnotationListResponse(**(response or {}))

    def list_system_annotations(
        self,
        date_from: Optional[List[str]] = None,
        date_to: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> SystemAnnotationListResponse:
        """List system annotations.

        Args:
            date_from: Optional list of start dates (YYYY-MM-DD)
            date_to: Optional list of end dates (YYYY-MM-DD)
            limit: Max number of items
            offset: Number of items to skip
        """
        params: Dict[str, Any] = {}

        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if date_from is not None:
            params["date_from"] = date_from
        if date_to is not None:
            params["date_to"] = date_to

        response = self.client.get(f"{self._SYSTEM_ANNOTATIONS_BASE}/", params=params)
        return SystemAnnotationListResponse(**(response or {}))

    def get_user_annotation(self, annotation_id: str, app_id: str) -> UserAnnotationSingleResponse:
        """
        Get a single user annotation.

        Args:
            annotation_id: Annotation UUID
            app_id: App UUID (required; sent as website_id query param)

        Returns:
            Dictionary with annotation
        """
        params = {"website_id": app_id}
        response = self.client.get(f"{self._USER_ANNOTATIONS_BASE}/{annotation_id}/", params=params)
        return UserAnnotationSingleResponse(**(response or {}))

    # No generic alias for get (user-only)

    def delete_user_annotation(self, annotation_id: str, app_id: str) -> None:
        """
        Delete a user annotation.

        Args:
            annotation_id: Annotation UUID
            app_id: App UUID (required; sent as website_id query param)

        Returns:
            None (204 No Content)
        """
        params = {"website_id": app_id}
        self.client.delete(f"{self._USER_ANNOTATIONS_BASE}/{annotation_id}/", params=params)

    # No generic alias for delete (user-only)

    def update_user_annotation(
        self,
        annotation_id: str,
        app_id: str,
        content: str,
        date: str,
        visibility: Optional[str] = "private",
    ) -> UserAnnotationSingleResponse:
        """
        Update an existing user annotation.

        Args:
            annotation_id: Annotation UUID
            app_id: App UUID (sent as website_id in API payload)
            content: Updated content (max 150 chars)
            date: Updated date (YYYY-MM-DD)
            visibility: "private" (default) or "public"

        Returns:
            Dictionary with updated annotation
        """
        attributes: Dict[str, Any] = {
            "website_id": app_id,
            "content": content,
            "date": date,
        }
        if visibility is not None:
            attributes["visibility"] = visibility

        data = {"data": {"type": "UserAnnotation", "id": annotation_id, "attributes": attributes}}
        response = self.client.patch(f"{self._USER_ANNOTATIONS_BASE}/{annotation_id}/", data=data)
        return UserAnnotationSingleResponse(**(response or {}))
