"""
Apps API for Piwik PRO.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

if TYPE_CHECKING:
    from ...client import PiwikProClient
from .models import (
    AppEditableAttributes,
    AppType,
    NewAppAttributes,
    Permission,
    SortOrder,
)


class AppsAPI:
    """Apps API client for Piwik PRO."""

    def __init__(self, client: "PiwikProClient"):
        """
        Initialize Apps API client.

        Args:
            client: Piwik PRO HTTP client instance
        """
        self.client = client

    def list_apps(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        search: Optional[str] = None,
        search_query: Optional[str] = None,  # deprecated
        sort: Optional[SortOrder] = None,
        permission: Optional[Permission] = None,
    ) -> Union[Dict[str, Any], None]:
        """
        Get list of apps.

        Args:
            offset: Sets offset for list of items (default: 0)
            limit: Limits the number of returned items (default: 10, max: 1000)
            search: App search query
            search_query: (deprecated) Use `search` param instead
            sort: Sort field (default: -addedAt)
            permission: Filter apps by permission

        Returns:
            Dictionary containing app list response

        Raises:
            PiwikProAPIError: If the request fails
        """
        params: Dict[str, Any] = {}

        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit
        if search is not None:
            params["search"] = search
        if search_query is not None:
            params["search_query"] = search_query
        if sort is not None:
            params["sort"] = sort.value
        if permission is not None:
            params["permission"] = permission.value

        return self.client.get("/api/apps/v2", params=params)

    def create_app(
        self,
        name: str,
        urls: List[str],
        app_id: Optional[str] = None,
        app_type: Optional[AppType] = None,
        **kwargs,
    ) -> Union[Dict[str, Any], None]:
        """
        Create a new app.

        Args:
            name: App name (max 90 characters)
            urls: List of URLs under which the app is available
            app_id: Optional UUID for the app
            app_type: App type (default: web)
            **kwargs: Additional app attributes (see AppEditableAttributes)

        Returns:
            Dictionary containing created app response

        Raises:
            PiwikProAPIError: If the request fails
        """
        attributes = NewAppAttributes(name=name, urls=urls, **kwargs)

        # Set optional fields
        if app_id is not None:
            attributes.id = app_id
        if app_type is not None:
            attributes.app_type = app_type

        data = {
            "data": {
                "type": "ppms/app",
                "attributes": attributes.model_dump(by_alias=True, exclude_none=True),
            }
        }

        return self.client.post("/api/apps/v2", data=data)

    def get_app(self, app_id: str) -> Union[Dict[str, Any], None]:
        """
        Get app details by ID.

        Args:
            app_id: App UUID

        Returns:
            Dictionary containing app details

        Raises:
            NotFoundError: If app is not found
            PiwikProAPIError: If the request fails
        """
        return self.client.get(f"/api/apps/v2/{app_id}")

    def update_app(
        self,
        app_id: str,
        **kwargs,
    ) -> None:
        """
        Update an existing app.

        Args:
            app_id: App UUID
            **kwargs: App attributes to update (see AppEditableAttributes)

        Returns:
            None (204 No Content)

        Raises:
            NotFoundError: If app is not found
            BadRequestError: If request data is invalid
            PiwikProAPIError: If the request fails
        """

        attributes = AppEditableAttributes(**kwargs)

        data = {
            "data": {
                "type": "ppms/app",
                "id": app_id,
                "attributes": attributes.model_dump(by_alias=True, exclude_none=True),
            }
        }

        self.client.patch(f"/api/apps/v2/{app_id}", data=data)

    def delete_app(self, app_id: str) -> None:
        """
        Delete an app by ID.

        Args:
            app_id: App UUID

        Returns:
            None (204 No Content)

        Raises:
            NotFoundError: If app is not found
            BadRequestError: If deletion is not allowed
            PiwikProAPIError: If the request fails
        """
        self.client.delete(f"/api/apps/v2/{app_id}")
