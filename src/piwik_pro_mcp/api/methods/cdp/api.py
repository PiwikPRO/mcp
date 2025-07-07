"""
CDP API for Piwik PRO.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Union

if TYPE_CHECKING:
    from ...client import PiwikProClient

from .models import EditableAudienceAttributes, NewAudienceAttributes


class CdpAPI:
    """CDP API client for Piwik PRO."""

    def __init__(self, client: "PiwikProClient"):
        """
        Initialize CDP API client.

        Args:
            client: Piwik PRO HTTP client instance
        """
        self.client = client

    def list_audiences(
        self,
        app_id: str,
    ) -> Union[Dict[str, Any], None]:
        """
        Get list of audiences for a specific app.

        Args:
            app_id: App UUID

        Returns:
            Array containing audience list

        Raises:
            PiwikProAPIError: If the request fails
        """
        return self.client.get(f"/api/cdp/settings/v1/app/{app_id}/audience")

    def get_audience(
        self,
        app_id: str,
        audience_id: str,
    ) -> Union[Dict[str, Any], None]:
        """
        Get audience details by ID.

        Args:
            app_id: App UUID
            audience_id: Audience UUID

        Returns:
            Dictionary containing audience details

        Raises:
            NotFoundError: If audience is not found
            PiwikProAPIError: If the request fails
        """
        return self.client.get(f"/api/cdp/settings/v1/app/{app_id}/audience/{audience_id}")

    def list_attributes(
        self,
        app_id: str,
    ) -> Union[List[Dict[str, Any]], None]:
        """
        Get list of all profile attributes available in CDP for a specific app.

        This endpoint returns detailed information about each attribute including:
        - Data type (string, number, datetime, etc.)
        - Supported value selectors (first, last, any)
        - Categories (Device, Location, Custom, etc.)
        - Scope (event or profile)

        Args:
            app_id: App UUID

        Returns:
            Array containing attribute list with metadata

        Raises:
            PiwikProAPIError: If the request fails
        """
        return self.client.get(f"/api/cdp/settings/v1/app/{app_id}/attribute")

    def create_audience(
        self,
        app_id: str,
        name: str,
        description: str,
        definition: Dict[str, Any],
        membership_duration_days: int,
        **kwargs,
    ) -> Union[Dict[str, Any], None]:
        """
        Create a new audience.

        Args:
            app_id: App UUID
            name: Audience name (max 100 characters)
            description: Audience description (max 200 characters)
            definition: Audience definition with conditions
            membership_duration_days: Duration in days for audience membership
            **kwargs: Additional audience attributes

        Returns:
            Dictionary containing created audience response

        Raises:
            PiwikProAPIError: If the request fails
        """
        attributes = NewAudienceAttributes(
            name=name,
            description=description,
            definition=definition,
            membership_duration_days=membership_duration_days,
            **kwargs,
        )

        data = attributes.model_dump(by_alias=True, exclude_none=True)

        return self.client.post(f"/api/cdp/settings/v1/app/{app_id}/audience", data=data)

    def update_audience(
        self,
        app_id: str,
        audience_id: str,
        name: str,
        description: str,
        definition: Dict[str, Any],
        membership_duration_days: int,
        **kwargs,
    ) -> Union[Dict[str, Any], None]:
        """
        Update an existing audience.

        Args:
            app_id: App UUID
            audience_id: Audience UUID to update
            name: Audience name (max 100 characters)
            description: Audience description (max 200 characters)
            definition: Audience definition with conditions
            membership_duration_days: Duration in days for audience membership
            **kwargs: Additional audience attributes

        Returns:
            Dictionary containing updated audience response

        Raises:
            NotFoundError: If audience is not found
            PiwikProAPIError: If the request fails
        """
        attributes = EditableAudienceAttributes(
            name=name,
            description=description,
            definition=definition,
            membership_duration_days=membership_duration_days,
            **kwargs,
        )

        # Handle definition field serialization
        attributes_dict = attributes.model_dump(by_alias=True, exclude_none=True)

        # Special handling for definition field to ensure proper serialization
        if attributes.definition is not None:
            attributes_dict["definition"] = attributes.definition.model_dump(
                mode="json", by_alias=True, exclude_none=True
            )

        return self.client.request(
            "PUT", f"/api/cdp/settings/v1/app/{app_id}/audience/{audience_id}", data=attributes_dict
        )

    def delete_audience(
        self,
        app_id: str,
        audience_id: str,
    ) -> Union[Dict[str, Any], None]:
        """
        Delete an existing audience.

        Args:
            app_id: App UUID
            audience_id: Audience UUID to delete

        Returns:
            Dictionary containing deletion confirmation or None for 204 responses

        Raises:
            NotFoundError: If audience is not found
            PiwikProAPIError: If the request fails
        """
        return self.client.delete(f"/api/cdp/settings/v1/app/{app_id}/audience/{audience_id}")
