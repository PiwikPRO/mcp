"""
Analytics API for Piwik PRO - User Annotations, Goals, and Custom Dimensions.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from piwik_pro_mcp.api.methods.analytics.models import (
    CustomDimensionListResponse,
    CustomDimensionSingleResponse,
    CustomDimensionSlotsResponse,
    DimensionsListResponse,
    DimensionValueGroupingListResponse,
    GoalListResponse,
    GoalSingleResponse,
    MetricsListResponse,
    ProductCustomDimensionListResponse,
    ProductCustomDimensionSingleResponse,
    QueryRequest,
    QueryResponse,
    SystemAnnotationListResponse,
    UserAnnotationListResponse,
    UserAnnotationSingleResponse,
)

if TYPE_CHECKING:
    from ...client import PiwikProClient


class AnalyticsAPI:
    """Analytics API client for Piwik PRO (annotations, goals, and custom dimensions)."""

    def __init__(self, client: "PiwikProClient"):
        """
        Initialize Analytics API client.

        Args:
            client: Piwik PRO HTTP client instance
        """
        self.client = client

    # Base endpoints
    _USER_ANNOTATIONS_BASE = "/api/analytics/v1/manage/annotation/user"
    _SYSTEM_ANNOTATIONS_BASE = "/api/analytics/v1/manage/annotation/system"
    _GOALS_BASE = "/api/analytics/v1/manage/goals"
    _QUERY_BASE = "/api/analytics/v1/query"
    _DIMENSIONS_ENDPOINT = "/analytics/api/engine/dimensions/"
    _METRICS_ENDPOINT = "/analytics/api/engine/metrics/"
    _CUSTOM_DIMENSIONS_BASE = "/api/analytics/v1/manage/custom-dimensions"
    _PRODUCT_CUSTOM_DIMENSIONS_BASE = "/api/analytics/v1/manage/product-custom-dimensions"
    _DIMENSION_VALUE_GROUPINGS_BASE = "/analytics/api/engine/dimension-value-groupings"

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
            app_id: App UUID
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

    # Goals methods

    def create_goal(
        self,
        website_id: str,
        name: str,
        trigger: str,
        revenue: str,
        description: Optional[str] = None,
        pattern_type: Optional[str] = None,
        pattern: Optional[str] = None,
        allow_multiple: Optional[bool] = None,
        case_sensitive: Optional[bool] = None,
    ) -> GoalSingleResponse:
        """
        Create a new goal for a website.

        Args:
            website_id: Website/App UUID
            name: Goal name
            trigger: Trigger type (url, title, event_name, event_category, event_action,
                     file, external_website, manually)
            revenue: Revenue value as string in monetary format (e.g., "10.22" or "0")
            description: Optional description (max 1024 chars)
            pattern_type: Condition operator (contains, exact, regex).
                         Required for all triggers except "manually"
            pattern: Condition value to match against.
                    Required for all triggers except "manually"
            allow_multiple: Whether goal can be converted more than once per visit
            case_sensitive: Whether pattern matching is case sensitive

        Returns:
            GoalSingleResponse with created goal
        """
        attributes: Dict[str, Any] = {
            "website_id": website_id,
            "name": name,
            "trigger": trigger,
            "revenue": revenue,
        }

        if description is not None:
            attributes["description"] = description
        if pattern_type is not None:
            attributes["pattern_type"] = pattern_type
        if pattern is not None:
            attributes["pattern"] = pattern
        if allow_multiple is not None:
            attributes["allow_multiple"] = allow_multiple
        if case_sensitive is not None:
            attributes["case_sensitive"] = case_sensitive

        data = {"data": {"type": "Goal", "attributes": attributes}}
        response = self.client.post(f"{self._GOALS_BASE}/", data=data)
        return GoalSingleResponse(**(response or {}))

    def list_goals(
        self,
        website_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> GoalListResponse:
        """
        List all goals for a website.

        Args:
            website_id: Website/App UUID (required; sent as website_id query param)
            limit: Maximum number of rows to return (default: 10, min: 1, max: 100000)
            offset: Number of rows to skip (default: 0, min: 0)

        Returns:
            GoalListResponse with goals list and meta
        """
        params: Dict[str, Any] = {"website_id": website_id}

        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset

        response = self.client.get(f"{self._GOALS_BASE}/", params=params)
        return GoalListResponse(**(response or {}))

    def get_goal(self, goal_id: str, website_id: str) -> GoalSingleResponse:
        """
        Get a specific goal by ID.

        Args:
            goal_id: Goal UUID
            website_id: Website/App UUID (required; sent as website_id query param)

        Returns:
            GoalSingleResponse with goal details
        """
        params = {"website_id": website_id}
        response = self.client.get(f"{self._GOALS_BASE}/{goal_id}/", params=params)
        return GoalSingleResponse(**(response or {}))

    def update_goal(
        self,
        goal_id: str,
        website_id: str,
        name: str,
        trigger: str,
        revenue: str,
        description: Optional[str] = None,
        pattern_type: Optional[str] = None,
        pattern: Optional[str] = None,
        allow_multiple: Optional[bool] = None,
        case_sensitive: Optional[bool] = None,
    ) -> GoalSingleResponse:
        """
        Update an existing goal.

        Args:
            goal_id: Goal UUID
            website_id: Website/App UUID
            name: Goal name
            trigger: Trigger type (url, title, event_name, event_category, event_action,
                     file, external_website, manually)
            revenue: Revenue value as string in monetary format (e.g., "10.22" or "0")
            description: Optional description (max 1024 chars)
            pattern_type: Condition operator (contains, exact, regex).
                         Required for all triggers except "manually"
            pattern: Condition value to match against.
                    Required for all triggers except "manually"
            allow_multiple: Whether goal can be converted more than once per visit
            case_sensitive: Whether pattern matching is case sensitive

        Returns:
            GoalSingleResponse with updated goal
        """
        attributes: Dict[str, Any] = {
            "website_id": website_id,
            "name": name,
            "trigger": trigger,
            "revenue": revenue,
        }

        if description is not None:
            attributes["description"] = description
        if pattern_type is not None:
            attributes["pattern_type"] = pattern_type
        if pattern is not None:
            attributes["pattern"] = pattern
        if allow_multiple is not None:
            attributes["allow_multiple"] = allow_multiple
        if case_sensitive is not None:
            attributes["case_sensitive"] = case_sensitive

        data = {"data": {"type": "Goal", "id": goal_id, "attributes": attributes}}
        response = self.client.put(f"{self._GOALS_BASE}/{goal_id}/", data=data)
        return GoalSingleResponse(**(response or {}))

    def delete_goal(self, goal_id: str, website_id: str) -> None:
        """
        Delete a goal.

        Args:
            goal_id: Goal UUID
            website_id: Website/App UUID (required; sent as website_id query param)

        Returns:
            None (204 No Content)
        """
        params = {"website_id": website_id}
        self.client.delete(f"{self._GOALS_BASE}/{goal_id}/", params=params)

    def execute_query(
        self,
        website_id: str,
        columns: list[dict[str, Any]],
        date_from: str | None = None,
        date_to: str | None = None,
        relative_date: str | None = None,
        filters: dict[str, Any] | None = None,
        metric_filters: dict[str, Any] | None = None,
        offset: int = 0,
        limit: int = 100,
        order_by: list[list[Any]] | None = None,
    ) -> QueryResponse:
        """
        Execute an analytics query.

        Args:
            website_id: Website/app UUID
            columns: List of column definitions with column_id and optional transformation_id
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            relative_date: Relative date (today, yesterday, last_week, last_month, last_year, last_X_days).
            filters: Optional dimension filter group with conditions
            metric_filters: Optional metric filter group with conditions
            offset: Number of rows to skip
            limit: Maximum rows to return
            order_by: Optional ordering specification

        Returns:
            Query response with data rows and metadata
        """
        # Validate request
        request = QueryRequest(
            website_id=website_id,
            columns=columns,
            date_from=date_from,
            date_to=date_to,
            relative_date=relative_date,
            filters=filters,
            metric_filters=metric_filters,
            offset=offset,
            limit=limit,
            order_by=order_by,
        )

        payload = request.model_dump(exclude_none=True)
        response = self.client.post(f"{self._QUERY_BASE}/", data=payload)

        return QueryResponse.model_validate(response)

    def list_dimensions(self, website_id: str) -> DimensionsListResponse:
        """
        List available dimensions for analytics queries.

        Args:
            website_id: UUID of the website/app

        Returns:
            List of dimension definitions with column_id, requires_events, and column_meta
        """
        params = {"website_id": website_id}
        # This endpoint returns plain JSON, not JSON:API format
        extra_headers = {"Accept": "application/json"}
        response = self.client.get(self._DIMENSIONS_ENDPOINT, params=params, extra_headers=extra_headers)
        return DimensionsListResponse.model_validate(response)

    def list_metrics(self, website_id: str) -> MetricsListResponse:
        """
        List available metrics for analytics queries.

        Args:
            website_id: UUID of the website/app

        Returns:
            List of metric definitions with column_id, requires_events, and column_meta
        """
        params = {"website_id": website_id}
        # This endpoint returns plain JSON, not JSON:API format
        extra_headers = {"Accept": "application/json"}
        response = self.client.get(self._METRICS_ENDPOINT, params=params, extra_headers=extra_headers)
        return MetricsListResponse.model_validate(response)

    # Custom Dimensions methods

    def create_custom_dimension(
        self,
        website_id: str,
        name: str,
        active: bool,
        case_sensitive: bool,
        scope: str,
        description: Optional[str] = None,
        slot: Optional[int] = None,
        extractions: Optional[List[Dict[str, str]]] = None,
    ) -> CustomDimensionSingleResponse:
        """
        Create a new standard custom dimension.

        Args:
            website_id: Website/App UUID
            name: Custom dimension name
            active: Whether dimension is active
            case_sensitive: Whether dimension is case sensitive
            scope: Dimension scope ("session" or "event")
            description: Optional description (max 300 chars)
            slot: Optional slot number (auto-assigned if not provided)
            extractions: Optional list of extraction configs.
                        Each extraction dict has "target" and "pattern" keys.

        Returns:
            CustomDimensionSingleResponse with created dimension
        """
        attributes: Dict[str, Any] = {
            "website_id": website_id,
            "name": name,
            "active": active,
            "case_sensitive": case_sensitive,
            "scope": scope,
        }

        if description is not None:
            attributes["description"] = description
        if slot is not None:
            attributes["slot"] = slot
        if extractions is not None:
            attributes["extractions"] = extractions

        data = {"data": {"type": "CustomDimension", "attributes": attributes}}
        response = self.client.post(f"{self._CUSTOM_DIMENSIONS_BASE}/", data=data)
        return CustomDimensionSingleResponse(**(response or {}))

    def list_custom_dimensions(
        self,
        website_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> CustomDimensionListResponse:
        """
        List all standard custom dimensions for a website.

        Args:
            website_id: Website/App UUID (required; sent as website_id query param)
            limit: Maximum number of rows to return (default: 10, min: 1, max: 100000)
            offset: Number of rows to skip (default: 0, min: 0)

        Returns:
            CustomDimensionListResponse with dimensions list and meta
        """
        params: Dict[str, Any] = {"website_id": website_id}

        params["limit"] = limit if limit is not None else 400  # max is 200 per scope type
        params["offset"] = offset if offset is not None else 0

        response = self.client.get(f"{self._CUSTOM_DIMENSIONS_BASE}/", params=params)
        return CustomDimensionListResponse(**(response or {}))

    def get_custom_dimension(self, dimension_id: str, website_id: str) -> CustomDimensionSingleResponse:
        """
        Get a specific standard custom dimension by ID.

        Args:
            dimension_id: Custom Dimension UUID
            website_id: Website/App UUID (required; sent as website_id query param)

        Returns:
            CustomDimensionSingleResponse with dimension details
        """
        params = {"website_id": website_id}
        response = self.client.get(f"{self._CUSTOM_DIMENSIONS_BASE}/{dimension_id}/", params=params)
        return CustomDimensionSingleResponse(**(response or {}))

    def update_custom_dimension(
        self,
        dimension_id: str,
        website_id: str,
        name: str,
        active: bool,
        case_sensitive: bool,
        description: Optional[str] = None,
        extractions: Optional[List[Dict[str, str]]] = None,
    ) -> CustomDimensionSingleResponse:
        """
        Update an existing standard custom dimension.

        Args:
            dimension_id: Custom Dimension UUID
            website_id: Website/App UUID
            name: Custom dimension name
            active: Whether dimension is active
            case_sensitive: Whether dimension is case sensitive
            scope: Dimension scope ("session" or "event")
            description: Optional description (max 300 chars)
            extractions: Optional list of extraction configs.
                        Each extraction dict has "target" and "pattern" keys.

        Returns:
            CustomDimensionSingleResponse with updated dimension
        """
        attributes: Dict[str, Any] = {
            "website_id": website_id,
            "name": name,
            "active": active,
            "case_sensitive": case_sensitive,
        }

        if description is not None:
            attributes["description"] = description
        if extractions is not None:
            attributes["extractions"] = extractions

        data = {"data": {"type": "CustomDimension", "id": dimension_id, "attributes": attributes}}
        response = self.client.put(f"{self._CUSTOM_DIMENSIONS_BASE}/{dimension_id}/", data=data)
        return CustomDimensionSingleResponse(**(response or {}))

    def get_custom_dimension_slots(
        self,
        website_id: str,
    ) -> CustomDimensionSlotsResponse:
        """
        Get slot availability statistics for all dimension types.

        Args:
            website_id: Website/App UUID (required; sent as website_id query param)

        Returns:
            CustomDimensionSlotsResponse with slot stats for session, event, and product dimensions
        """
        params = {"website_id": website_id}
        response = self.client.get(f"{self._CUSTOM_DIMENSIONS_BASE}/slots/", params=params)
        return CustomDimensionSlotsResponse(**(response or {}))

    def create_product_custom_dimension(
        self,
        website_id: str,
        name: str,
        slot: int,
        description: Optional[str] = None,
    ) -> ProductCustomDimensionSingleResponse:
        """
        Create a new product custom dimension.

        Args:
            website_id: Website/App UUID
            name: Product custom dimension name
            slot: Slot number (required, must be explicitly specified)
            description: Optional description (max 300 chars)

        Returns:
            ProductCustomDimensionSingleResponse with created dimension
        """
        attributes: Dict[str, Any] = {
            "website_id": website_id,
            "name": name,
            "slot": slot,
        }

        if description is not None:
            attributes["description"] = description

        data = {"data": {"type": "ProductCustomDimension", "attributes": attributes}}
        response = self.client.post(f"{self._PRODUCT_CUSTOM_DIMENSIONS_BASE}/", data=data)
        return ProductCustomDimensionSingleResponse(**(response or {}))

    def list_product_custom_dimensions(
        self,
        website_id: str,
    ) -> ProductCustomDimensionListResponse:
        """
        List all product custom dimensions for a website.

        Args:
            website_id: Website/App UUID (required; sent as website_id query param)

        Returns:
            ProductCustomDimensionListResponse with dimensions list and meta
        """
        params: Dict[str, Any] = {"website_id": website_id}
        response = self.client.get(f"{self._PRODUCT_CUSTOM_DIMENSIONS_BASE}/", params=params)
        return ProductCustomDimensionListResponse(**(response or {}))

    def get_product_custom_dimension(self, dimension_id: str, website_id: str) -> ProductCustomDimensionSingleResponse:
        """
        Get a specific product custom dimension by ID.

        Args:
            dimension_id: Product Custom Dimension UUID
            website_id: Website/App UUID (required; sent as website_id query param)

        Returns:
            ProductCustomDimensionSingleResponse with dimension details
        """
        params = {"website_id": website_id}
        response = self.client.get(f"{self._PRODUCT_CUSTOM_DIMENSIONS_BASE}/{dimension_id}/", params=params)
        return ProductCustomDimensionSingleResponse(**(response or {}))

    def update_product_custom_dimension(
        self,
        dimension_id: str,
        website_id: str,
        name: str,
        description: Optional[str] = None,
    ) -> ProductCustomDimensionSingleResponse:
        """
        Update an existing product custom dimension.

        Note: The slot number CANNOT be changed after creation. Only name and description
        can be updated.

        Args:
            dimension_id: Product Custom Dimension UUID
            website_id: Website/App UUID
            name: Product custom dimension name
            description: Optional description (max 300 chars)

        Returns:
            ProductCustomDimensionSingleResponse with updated dimension
        """
        attributes: Dict[str, Any] = {
            "website_id": website_id,
            "name": name,
        }

        if description is not None:
            attributes["description"] = description

        data = {"data": {"type": "ProductCustomDimension", "id": dimension_id, "attributes": attributes}}
        response = self.client.put(f"{self._PRODUCT_CUSTOM_DIMENSIONS_BASE}/{dimension_id}/", data=data)

        return ProductCustomDimensionSingleResponse(**(response or {}))

    def list_dimension_value_groupings(self, website_id: str) -> DimensionValueGroupingListResponse:
        """
        List dimension value groupings for a website.

        Args:
            website_id: Website/App UUID

        Returns:
            DimensionValueGroupingListResponse with count and results
        """
        # This endpoint returns plain JSON, not JSON:API format
        extra_headers = {"Accept": "application/json"}
        response = self.client.get(
            self._DIMENSION_VALUE_GROUPINGS_BASE, params={"website_id": website_id}, extra_headers=extra_headers
        )
        return DimensionValueGroupingListResponse.model_validate(response)
