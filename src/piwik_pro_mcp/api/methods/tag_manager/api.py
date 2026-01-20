"""
Tag Manager API for Piwik PRO.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union
from uuid import uuid4

if TYPE_CHECKING:
    from ...client import PiwikProClient
from .models import (
    DebugLinkAttributes,
    TagAttributes,
    TagFilters,
    TagManagerSortOrder,
    TriggerAttributes,
    TriggerCondition,
    TriggerFilters,
    VariableAttributes,
    VariableFilters,
    VersionType,
)


class TagManagerAPI:
    """Tag Manager API client for Piwik PRO."""

    def __init__(self, client: "PiwikProClient"):
        """
        Initialize Tag Manager API client.

        Args:
            client: Piwik PRO HTTP client instance
        """
        self.client = client

    def list_tags(
        self,
        app_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[TagManagerSortOrder] = None,
        filters: Optional[TagFilters] = None,
    ) -> Union[Dict[str, Any], None]:
        """
        Get list of tags for an app.

        Args:
            app_id: App UUID
            limit: Limits the number of returned items (default: 10)
            offset: Sets offset for list of items (default: 0)
            sort: Sort order
            filter: Filter by name, is_active, template, consent_type, is_prioritized, has_any_triggers

        Returns:
            Dictionary containing tag list response

        Raises:
            PiwikProAPIError: If the request fails
        """
        params: Dict[str, Any] = {}

        if limit is not None:
            params["page[limit]"] = limit
        if offset is not None:
            params["page[offset]"] = offset
        if sort is not None:
            params["sort"] = sort.value
        if filters is not None:
            for filter_type, value in filters.model_dump(by_alias=True, exclude_none=True).items():
                # Booleans should be serialized as lowercase strings in query params
                if isinstance(value, bool):
                    params[f"filter[{filter_type}]"] = str(value).lower()
                else:
                    params[f"filter[{filter_type}]"] = value

        return self.client.get(f"/api/tag/v1/{app_id}/tags", params=params)

    def create_tag(
        self,
        app_id: str,
        name: str,
        template: str,
        trigger_ids: Optional[List[str]] = None,
        **kwargs,
    ) -> Union[Dict[str, Any], None]:
        """
        Create a new tag.

        Args:
            app_id: App UUID
            name: Tag name
            template: Tag template
            trigger_ids: List of trigger UUIDs to attach to this tag (optional)
            **kwargs: Additional tag attributes

        Returns:
            Dictionary containing created tag response

        Raises:
            PiwikProAPIError: If the request fails

        Note:
            When using is_active parameter, ensure your Pydantic version correctly serializes
            field aliases. In Pydantic v2, use model_dump() instead of dict().
        """
        attributes = TagAttributes(name=name, template=template, **kwargs)

        data = {
            "data": {
                "type": "tag",
                "attributes": attributes.model_dump(by_alias=True, exclude_none=True),
            }
        }

        # Add relationships if trigger_ids are provided
        if trigger_ids:
            data["data"]["relationships"] = {
                "triggers": {"data": [{"id": trigger_id, "type": "trigger"} for trigger_id in trigger_ids]}
            }

        return self.client.post(f"/api/tag/v1/{app_id}/tags", data=data)

    def get_tag(self, app_id: str, tag_id: str) -> Union[Dict[str, Any], None]:
        """
        Get tag details by ID.

        Args:
            app_id: App UUID
            tag_id: Tag UUID

        Returns:
            Dictionary containing tag details

        Raises:
            NotFoundError: If tag is not found
            PiwikProAPIError: If the request fails
        """
        return self.client.get(f"/api/tag/v1/{app_id}/tags/{tag_id}")

    def get_tag_triggers(
        self,
        app_id: str,
        tag_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        **filters,
    ) -> Union[Dict[str, Any], None]:
        """
        Get list of triggers attached to a specific tag.

        Args:
            app_id: App UUID
            tag_id: Tag UUID
            limit: Number of results to return
            offset: Number of results to skip
            sort: Sort field and direction (e.g., 'name', '-created_at')
            **filters: Additional filters (name, trigger_type, etc.)

        Returns:
            Dictionary containing list of triggers attached to the tag

        Raises:
            NotFoundError: If tag is not found
            PiwikProAPIError: If the request fails
        """
        params = {}

        if limit is not None:
            params["page[limit]"] = limit
        if offset is not None:
            params["page[offset]"] = offset
        if sort is not None:
            params["sort"] = sort

        # Add filters
        for key, value in filters.items():
            if value is not None:
                params[f"filter[{key}]"] = value

        return self.client.get(f"/api/tag/v1/{app_id}/tags/{tag_id}/triggers", params=params)

    def get_trigger_tags(
        self,
        app_id: str,
        trigger_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        **filters,
    ) -> Union[Dict[str, Any], None]:
        """
        Get list of tags assigned to a specific trigger.

        Args:
            app_id: App UUID
            trigger_id: Trigger UUID
            limit: Number of results to return
            offset: Number of results to skip
            sort: Sort field and direction (e.g., 'name', '-created_at')
            **filters: Additional filters (name, is_active, template, consent_type, is_prioritized)

        Returns:
            Dictionary containing list of tags assigned to the trigger

        Raises:
            BadRequestError: If request parameters are invalid
            NotFoundError: If app or trigger not found
            APIError: If request fails
        """
        params = {}
        if limit is not None:
            params["page[limit]"] = limit
        if offset is not None:
            params["page[offset]"] = offset
        if sort is not None:
            params["sort"] = sort

        # Add filters
        for key, value in filters.items():
            if value is not None:
                params[f"filter[{key}]"] = value

        return self.client.get(f"/api/tag/v1/{app_id}/triggers/{trigger_id}/tags", params=params)

    def update_tag(
        self,
        app_id: str,
        tag_id: str,
        trigger_ids: Optional[List[str]] = None,
        **kwargs,
    ) -> Union[Dict[str, Any], None]:
        """
        Update an existing tag.

        Args:
            app_id: App UUID
            tag_id: Tag UUID
            trigger_ids: List of trigger UUIDs to attach to this tag (optional, replaces existing triggers)
            **kwargs: Tag attributes to update

        Returns:
            Dictionary containing updated tag

        Raises:
            NotFoundError: If tag is not found
            BadRequestError: If request data is invalid
            PiwikProAPIError: If the request fails

        Note:
            When using is_active parameter, ensure your Pydantic version correctly serializes
            field aliases. In Pydantic v2, use model_dump() instead of dict().
        """
        attributes = TagAttributes(**kwargs)

        editable_only = attributes.model_dump(
            by_alias=True,
            exclude_none=True,
            exclude={
                # Read-only fields (auto-generated by API)
                "createdAt",
                "created_at",
                "updatedAt",
                "updated_at",
                "is_published",
                # Create-only fields (immutable after creation)
                "template",
                "tag_type",
            },
        )
        data = {
            "data": {
                "type": "tag",
                "id": tag_id,
                "attributes": editable_only,
            }
        }

        # Add relationships if trigger_ids are provided
        if trigger_ids is not None:
            data["data"]["relationships"] = {
                "triggers": {"data": [{"id": trigger_id, "type": "trigger"} for trigger_id in trigger_ids]}
            }

        return self.client.patch(f"/api/tag/v1/{app_id}/tags/{tag_id}", data=data)

    def delete_tag(self, app_id: str, tag_id: str) -> None:
        """
        Delete a tag by ID.

        Args:
            app_id: App UUID
            tag_id: Tag UUID

        Returns:
            None (204 No Content)

        Raises:
            NotFoundError: If tag is not found
            BadRequestError: If deletion is not allowed
            PiwikProAPIError: If the request fails
        """
        self.client.delete(f"/api/tag/v1/{app_id}/tags/{tag_id}")

    def copy_tag(
        self,
        app_id: str,
        tag_id: str,
        name: Optional[str] = None,
        target_app_id: Optional[str] = None,
        with_triggers: bool = False,
    ) -> Union[Dict[str, Any], None]:
        """
        Copy a tag.

        Args:
            app_id: App UUID
            tag_id: Tag UUID to copy
            name: Optional new name for the copied tag
            target_app_id: Optional target App UUID to copy into (cross-app copy)
            with_triggers: Whether to copy tag with its triggers (tag-only option)

        Returns:
            Dictionary containing copied tag response

        Raises:
            NotFoundError: If tag is not found
            PiwikProAPIError: If the request fails
        """
        attributes: Dict[str, Any] = {"with_triggers": with_triggers}
        if name is not None:
            attributes["name"] = name

        data: Dict[str, Any] = {"data": {"type": "tag", "attributes": attributes}}

        if target_app_id is not None:
            data["data"]["relationships"] = {"target_app": {"data": {"id": target_app_id, "type": "app"}}}

        return self.client.post(f"/api/tag/v1/{app_id}/tags/{tag_id}/copy", data=data)

    # Triggers API

    def list_triggers(
        self,
        app_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[TagManagerSortOrder] = None,
        filters: Optional[TriggerFilters] = None,
    ) -> Union[Dict[str, Any], None]:
        """
        Get list of triggers for an app.

        Args:
            app_id: App UUID
            limit: Limits the number of returned items (default: 10)
            offset: Sets offset for list of items (default: 0)
            sort: Sort order
            filter_template: Filter by template names
            filter_is_active: Filter by active status

        Returns:
            Dictionary containing trigger list response

        Raises:
            PiwikProAPIError: If the request fails
        """
        params: Dict[str, Any] = {}

        if limit is not None:
            params["page[limit]"] = limit
        if offset is not None:
            params["page[offset]"] = offset
        if sort is not None:
            params["sort"] = sort.value
        if filters is not None:
            for filter_type, value in filters.model_dump(by_alias=True, exclude_none=True).items():
                # Booleans should be serialized as lowercase strings in query params
                if isinstance(value, bool):
                    params[f"filter[{filter_type}]"] = str(value).lower()
                else:
                    params[f"filter[{filter_type}]"] = value

        return self.client.get(f"/api/tag/v1/{app_id}/triggers", params=params)

    def create_trigger(
        self,
        app_id: str,
        name: str,
        trigger_type: str,
        **kwargs,
    ) -> Union[Dict[str, Any], None]:
        """
        Create a new trigger.

        Args:
            app_id: App UUID
            name: Trigger name
            trigger_type: Trigger type (page_view, click, etc.)
            **kwargs: Additional trigger attributes

        Returns:
            Dictionary containing created trigger response

        Raises:
            PiwikProAPIError: If the request fails
        """
        # Generate unique condition_id for each condition while creating the trigger
        conditions = kwargs.get("conditions")
        if conditions:
            normalized_conditions = []
            for condition in conditions:
                if isinstance(condition, TriggerCondition):
                    condition_data = condition.model_dump()
                elif isinstance(condition, dict):
                    condition_data = condition.copy()
                else:
                    condition_data = dict(condition)

                if not condition_data.get("condition_id"):
                    condition_data["condition_id"] = str(uuid4())
                normalized_conditions.append(condition_data)

            kwargs["conditions"] = normalized_conditions

        attributes = TriggerAttributes(name=name, trigger_type=trigger_type, **kwargs)

        data = {
            "data": {
                "type": "trigger",
                "attributes": attributes.model_dump(by_alias=True, exclude_none=True),
            }
        }

        return self.client.post(f"/api/tag/v1/{app_id}/triggers", data=data)

    def get_trigger(self, app_id: str, trigger_id: str) -> Union[Dict[str, Any], None]:
        """
        Get trigger details by ID.

        Args:
            app_id: App UUID
            trigger_id: Trigger UUID

        Returns:
            Dictionary containing trigger details

        Raises:
            NotFoundError: If trigger is not found
            PiwikProAPIError: If the request fails
        """
        return self.client.get(f"/api/tag/v1/{app_id}/triggers/{trigger_id}")

    def update_trigger(
        self,
        app_id: str,
        trigger_id: str,
        **kwargs,
    ) -> Union[Dict[str, Any], None]:
        """
        Update an existing trigger.

        Args:
            app_id: App UUID
            trigger_id: Trigger UUID
            **kwargs: Trigger attributes to update

        Returns:
            Dictionary containing updated trigger

        Raises:
            NotFoundError: If trigger is not found
            BadRequestError: If request data is invalid
            PiwikProAPIError: If the request fails
        """
        attributes = TriggerAttributes(**kwargs)

        data = {
            "data": {
                "type": "trigger",
                "id": trigger_id,
                "attributes": attributes.model_dump(by_alias=True, exclude_none=True),
            }
        }

        return self.client.patch(f"/api/tag/v1/{app_id}/triggers/{trigger_id}", data=data)

    def delete_trigger(self, app_id: str, trigger_id: str) -> None:
        """
        Delete a trigger by ID.

        Args:
            app_id: App UUID
            trigger_id: Trigger UUID

        Returns:
            None (204 No Content)

        Raises:
            NotFoundError: If trigger is not found
            BadRequestError: If deletion is not allowed
            PiwikProAPIError: If the request fails
        """
        self.client.delete(f"/api/tag/v1/{app_id}/triggers/{trigger_id}")

    def copy_trigger(
        self,
        app_id: str,
        trigger_id: str,
        name: Optional[str] = None,
        target_app_id: Optional[str] = None,
    ) -> Union[Dict[str, Any], None]:
        """
        Copy a trigger.

        Args:
            app_id: App UUID
            trigger_id: Trigger UUID to copy
            name: Optional new name for the copied trigger
            target_app_id: Optional target App UUID to copy into (cross-app copy)

        Returns:
            Dictionary containing copied trigger response

        Raises:
            NotFoundError: If trigger is not found
            PiwikProAPIError: If the request fails
        """
        data: Dict[str, Any] = {"data": {"type": "trigger"}}

        if name is not None:
            data["data"]["attributes"] = {"name": name}

        if target_app_id is not None:
            data["data"]["relationships"] = {"target_app": {"data": {"id": target_app_id, "type": "app"}}}

        return self.client.post(f"/api/tag/v1/{app_id}/triggers/{trigger_id}/copy", data=data)

    # Variables API

    def list_variables(
        self,
        app_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[TagManagerSortOrder] = None,
        filters: Optional[VariableFilters] = None,
    ) -> Union[Dict[str, Any], None]:
        """
        Get list of variables for an app.

        Args:
            app_id: App UUID
            limit: Limits the number of returned items (default: 10)
            offset: Sets offset for list of items (default: 0)
            sort: Sort order
            filter_template: Filter by template names
            filter_is_active: Filter by active status

        Returns:
            Dictionary containing variable list response

        Raises:
            PiwikProAPIError: If the request fails
        """
        params: Dict[str, Any] = {}

        if limit is not None:
            params["page[limit]"] = limit
        if offset is not None:
            params["page[offset]"] = offset
        if sort is not None:
            params["sort"] = sort.value
        if filters is not None:
            for filter_type, value in filters.model_dump(by_alias=True, exclude_none=True).items():
                # Booleans should be serialized as lowercase strings in query params
                if isinstance(value, bool):
                    params[f"filter[{filter_type}]"] = str(value).lower()
                else:
                    params[f"filter[{filter_type}]"] = value

        return self.client.get(f"/api/tag/v1/{app_id}/variables", params=params)

    def create_variable(
        self,
        app_id: str,
        name: str,
        variable_type: str,
        **kwargs,
    ) -> Union[Dict[str, Any], None]:
        """
        Create a new variable.

        Args:
            app_id: App UUID
            name: Variable name
            variable_type: Variable type
            **kwargs: Additional variable attributes

        Returns:
            Dictionary containing created variable response

        Raises:
            PiwikProAPIError: If the request fails
        """
        attributes = VariableAttributes(name=name, variable_type=variable_type, **kwargs)

        data = {
            "data": {
                "type": "variable",
                "attributes": attributes.model_dump(by_alias=True, exclude_none=True),
            }
        }

        return self.client.post(f"/api/tag/v1/{app_id}/variables", data=data)

    def get_variable(self, app_id: str, variable_id: str) -> Union[Dict[str, Any], None]:
        """
        Get variable details by ID.

        Args:
            app_id: App UUID
            variable_id: Variable UUID

        Returns:
            Dictionary containing variable details

        Raises:
            NotFoundError: If variable is not found
            PiwikProAPIError: If the request fails
        """
        return self.client.get(f"/api/tag/v1/{app_id}/variables/{variable_id}")

    def update_variable(
        self,
        app_id: str,
        variable_id: str,
        **kwargs,
    ) -> Union[Dict[str, Any], None]:
        """
        Update an existing variable.

        Args:
            app_id: App UUID
            variable_id: Variable UUID
            **kwargs: Variable attributes to update

        Returns:
            Dictionary containing updated variable

        Raises:
            NotFoundError: If variable is not found
            BadRequestError: If request data is invalid
            PiwikProAPIError: If the request fails
        """
        attributes = VariableAttributes(**kwargs)

        data = {
            "data": {
                "type": "variable",
                "id": variable_id,
                "attributes": attributes.model_dump(by_alias=True, exclude_none=True),
            }
        }

        return self.client.patch(f"/api/tag/v1/{app_id}/variables/{variable_id}", data=data)

    def delete_variable(self, app_id: str, variable_id: str) -> None:
        """
        Delete a variable by ID.

        Args:
            app_id: App UUID
            variable_id: Variable UUID

        Returns:
            None (204 No Content)

        Raises:
            NotFoundError: If variable is not found
            BadRequestError: If deletion is not allowed
            PiwikProAPIError: If the request fails
        """
        self.client.delete(f"/api/tag/v1/{app_id}/variables/{variable_id}")

    def copy_variable(
        self,
        app_id: str,
        variable_id: str,
        name: Optional[str] = None,
        target_app_id: Optional[str] = None,
    ) -> Union[Dict[str, Any], None]:
        """
        Copy a variable.

        Args:
            app_id: App UUID
            variable_id: Variable UUID to copy
            name: Optional new name for the copied variable
            target_app_id: Optional target App UUID to copy into (cross-app copy)

        Returns:
            Dictionary containing copied variable response

        Raises:
            NotFoundError: If variable is not found
            PiwikProAPIError: If the request fails
        """
        data: Dict[str, Any] = {"data": {"type": "variable"}}

        if name is not None:
            data["data"]["attributes"] = {"name": name}

        if target_app_id is not None:
            data["data"]["relationships"] = {"target_app": {"data": {"id": target_app_id, "type": "app"}}}

        return self.client.post(f"/api/tag/v1/{app_id}/variables/{variable_id}/copy", data=data)

    # Versions API

    def list_versions(
        self,
        app_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[TagManagerSortOrder] = None,
        filter_version_type: Optional[VersionType] = None,
    ) -> Union[Dict[str, Any], None]:
        """
        Get list of versions for an app.

        Args:
            app_id: App UUID
            limit: Limits the number of returned items (default: 10)
            offset: Sets offset for list of items (default: 0)
            sort: Sort order
            filter_version_type: Filter by version type

        Returns:
            Dictionary containing version list response

        Raises:
            PiwikProAPIError: If the request fails
        """
        params: Dict[str, Any] = {}

        if limit is not None:
            params["page[limit]"] = limit
        if offset is not None:
            params["page[offset]"] = offset
        if sort is not None:
            params["sort"] = sort.value
        if filter_version_type is not None:
            params["filter[version_type]"] = filter_version_type.value

        return self.client.get(f"/api/tag/v1/{app_id}/versions", params=params)

    def get_version(self, app_id: str, version_id: str) -> Union[Dict[str, Any], None]:
        """
        Get version details by ID.

        Args:
            app_id: App UUID
            version_id: Version UUID

        Returns:
            Dictionary containing version details

        Raises:
            NotFoundError: If version is not found
            PiwikProAPIError: If the request fails
        """
        return self.client.get(f"/api/tag/v1/{app_id}/versions/{version_id}")

    def get_draft_version(self, app_id: str) -> Union[Dict[str, Any], None]:
        """
        Get draft version for an app.

        Args:
            app_id: App UUID

        Returns:
            Dictionary containing draft version details

        Raises:
            NotFoundError: If draft version is not found
            PiwikProAPIError: If the request fails
        """
        return self.client.get(f"/api/tag/v1/{app_id}/versions/draft")

    def get_published_version(self, app_id: str) -> Union[Dict[str, Any], None]:
        """
        Get published version for an app.

        Args:
            app_id: App UUID

        Returns:
            Dictionary containing published version details

        Raises:
            NotFoundError: If published version is not found
            PiwikProAPIError: If the request fails
        """
        return self.client.get(f"/api/tag/v1/{app_id}/versions/published")

    def publish_draft_version(self, app_id: str) -> Union[Dict[str, Any], None]:
        """
        Publish the draft version.

        Args:
            app_id: App UUID

        Returns:
            Dictionary containing operation response

        Raises:
            BadRequestError: If publish operation is not allowed
            PiwikProAPIError: If the request fails
        """
        return self.client.post(f"/api/tag/v1/{app_id}/versions/draft/publish")

    def publish_version(self, app_id: str, version_id: str) -> Union[Dict[str, Any], None]:
        """
        Publish a specific version.

        Args:
            app_id: App UUID
            version_id: Version UUID to publish

        Returns:
            Dictionary containing operation response

        Raises:
            NotFoundError: If version is not found
            BadRequestError: If publish operation is not allowed
            PiwikProAPIError: If the request fails
        """
        return self.client.post(f"/api/tag/v1/{app_id}/versions/{version_id}/publish")

    def restore_published_version(self, app_id: str) -> Union[Dict[str, Any], None]:
        """
        Restore the published version to draft.

        Args:
            app_id: App UUID

        Returns:
            Dictionary containing operation response

        Raises:
            BadRequestError: If restore operation is not allowed
            PiwikProAPIError: If the request fails
        """
        return self.client.post(f"/api/tag/v1/{app_id}/versions/published/restore")

    def restore_version(self, app_id: str, version_id: str) -> Union[Dict[str, Any], None]:
        """
        Restore a specific version to draft.

        Args:
            app_id: App UUID
            version_id: Version UUID to restore

        Returns:
            Dictionary containing operation response

        Raises:
            NotFoundError: If version is not found
            BadRequestError: If restore operation is not allowed
            PiwikProAPIError: If the request fails
        """
        return self.client.post(f"/api/tag/v1/{app_id}/versions/{version_id}/restore")

    def create_draft_snapshot(self, app_id: str, name: str) -> Union[Dict[str, Any], None]:
        """
        Create a snapshot of the draft version.

        Args:
            app_id: App UUID
            name: Snapshot name

        Returns:
            Dictionary containing operation response

        Raises:
            BadRequestError: If snapshot operation is not allowed
            PiwikProAPIError: If the request fails
        """
        data = {"data": {"type": "version", "attributes": {"name": name}}}

        return self.client.post(f"/api/tag/v1/{app_id}/versions/draft/snapshot", data=data)

    # Debug Links API

    def list_debug_links(
        self,
        app_id: str,
        version_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Union[Dict[str, Any], None]:
        """
        Get list of debug links for a version.

        Args:
            app_id: App UUID
            version_id: Version UUID
            limit: Limits the number of returned items (default: 10)
            offset: Sets offset for list of items (default: 0)

        Returns:
            Dictionary containing debug link list response

        Raises:
            PiwikProAPIError: If the request fails
        """
        params: Dict[str, Any] = {}

        if limit is not None:
            params["page[limit]"] = limit
        if offset is not None:
            params["page[offset]"] = offset

        return self.client.get(f"/api/tag/v1/{app_id}/versions/{version_id}/debug-links", params=params)

    def create_debug_link(
        self,
        app_id: str,
        version_id: str,
        name: str,
        url: str,
        **kwargs,
    ) -> Union[Dict[str, Any], None]:
        """
        Create a debug link for a version.

        Args:
            app_id: App UUID
            version_id: Version UUID
            name: Debug link name
            url: Debug link URL
            **kwargs: Additional debug link attributes

        Returns:
            Dictionary containing created debug link response

        Raises:
            PiwikProAPIError: If the request fails
        """
        attributes = DebugLinkAttributes(name=name, url=url, **kwargs)

        data = {
            "data": {
                "type": "debug-link",
                "attributes": attributes.model_dump(by_alias=True, exclude_none=True),
            }
        }

        return self.client.post(f"/api/tag/v1/{app_id}/versions/{version_id}/debug-links", data=data)

    def get_debug_link(self, app_id: str, version_id: str, debug_link_id: str) -> Union[Dict[str, Any], None]:
        """
        Get debug link details by ID.

        Args:
            app_id: App UUID
            version_id: Version UUID
            debug_link_id: Debug link UUID

        Returns:
            Dictionary containing debug link details

        Raises:
            NotFoundError: If debug link is not found
            PiwikProAPIError: If the request fails
        """
        return self.client.get(f"/api/tag/v1/{app_id}/versions/{version_id}/debug-links/{debug_link_id}")

    def delete_debug_link(self, app_id: str, version_id: str, debug_link_id: str) -> None:
        """
        Delete a debug link by ID.

        Args:
            app_id: App UUID
            version_id: Version UUID
            debug_link_id: Debug link UUID

        Returns:
            None (204 No Content)

        Raises:
            NotFoundError: If debug link is not found
            PiwikProAPIError: If the request fails
        """
        self.client.delete(f"/api/tag/v1/{app_id}/versions/{version_id}/debug-links/{debug_link_id}")

    # Operations API

    def get_operation(self, app_id: str, operation_id: str) -> Union[Dict[str, Any], None]:
        """
        Get operation details by ID.

        Args:
            app_id: App UUID
            operation_id: Operation UUID

        Returns:
            Dictionary containing operation details

        Raises:
            NotFoundError: If operation is not found
            PiwikProAPIError: If the request fails
        """
        return self.client.get(f"/api/tag/v1/{app_id}/operations/{operation_id}")

    # Import/Export API

    def import_version(self, app_id: str, import_data: Dict[str, Any]) -> Union[Dict[str, Any], None]:
        """
        Import version data.

        Args:
            app_id: App UUID
            import_data: Version data to import

        Returns:
            Dictionary containing import operation response

        Raises:
            BadRequestError: If import data is invalid
            PiwikProAPIError: If the request fails
        """
        return self.client.post(f"/api/tag/v1/{app_id}/versions/import", data=import_data)

    def export_version_files(self, app_id: str, version_id: str) -> Union[Dict[str, Any], None]:
        """
        Export version files.

        Args:
            app_id: App UUID
            version_id: Version UUID to export

        Returns:
            Dictionary containing export operation response

        Raises:
            NotFoundError: If version is not found
            PiwikProAPIError: If the request fails
        """
        return self.client.post(f"/api/tag/v1/{app_id}/versions/{version_id}/export-files")

    def get_export_file(self, app_id: str, version_id: str, export_file_id: str) -> Union[Dict[str, Any], None]:
        """
        Get export file details.

        Args:
            app_id: App UUID
            version_id: Version UUID
            export_file_id: Export file UUID

        Returns:
            Dictionary containing export file details

        Raises:
            NotFoundError: If export file is not found
            PiwikProAPIError: If the request fails
        """
        return self.client.get(f"/api/tag/v1/{app_id}/versions/{version_id}/export-files/{export_file_id}")
