"""
CDP audience management functions.

This module provides functionality for creating, listing, and retrieving
CDP audiences, with proper error handling and response formatting.
"""

from piwik_pro_mcp.api.exceptions import BadRequestError, NotFoundError
from piwik_pro_mcp.api.methods.cdp.models import EditableAudienceAttributes, NewAudienceAttributes
from piwik_pro_mcp.responses import OperationStatusResponse

from ...common.utils import create_piwik_client, validate_data_against_model
from .models import (
    AudienceCreateMCPResponse,
    AudienceDetailsMCPResponse,
    AudienceListMCPResponse,
    AudienceSummary,
    AudienceUpdateMCPResponse,
)


def list_audiences(app_id: str) -> AudienceListMCPResponse:
    """
    List audiences from Piwik PRO CDP.

    Retrieves a list of audiences that are configured in the Piwik PRO
    Customer Data Platform for the specified app.

    Args:
        app_id: UUID of the app to list audiences for

    Returns:
        Dictionary containing audience list and metadata

    Raises:
        RuntimeError: If authentication fails or API request fails
    """
    try:
        client = create_piwik_client()
        response = client.cdp.list_audiences(app_id=app_id)

        # Extract relevant information and convert to AudienceSummary models
        audiences_data = []
        for audience in response or []:
            audience_summary = AudienceSummary(
                id=audience.get("id", ""),
                name=audience.get("name", ""),
                description=audience.get("description", ""),
                membership_duration_days=audience.get("membership_duration_days", 30),
                version=audience.get("version", 1),
                created_at=audience.get("created_at"),
                updated_at=audience.get("updated_at"),
                is_author=audience.get("is_author", False),
            )
            audiences_data.append(audience_summary)

        return AudienceListMCPResponse(
            audiences=audiences_data,
            total=len(audiences_data),
        )

    except (BadRequestError, NotFoundError) as e:
        raise RuntimeError(f"Failed to list audiences: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error listing audiences: {e}")


def get_audience_details(app_id: str, audience_id: str) -> AudienceDetailsMCPResponse:
    """
    Get detailed information about a specific audience.

    Args:
        app_id: UUID of the app
        audience_id: UUID of the audience to retrieve

    Returns:
        Dictionary containing detailed audience information

    Raises:
        RuntimeError: If authentication fails, audience not found, or API request fails
    """
    try:
        client = create_piwik_client()
        response = client.cdp.get_audience(app_id=app_id, audience_id=audience_id)

        if not response:
            raise RuntimeError(f"Audience {audience_id} not found")

        return AudienceDetailsMCPResponse(
            id=response.get("id", ""),
            name=response.get("name", ""),
            description=response.get("description", ""),
            membership_duration_days=response.get("membership_duration_days", 30),
            version=response.get("version", 1),
            definition=response.get("definition", {}),
            author_email=response.get("author", {}).get("email", ""),
            is_author=response.get("is_author", False),
            created_at=response.get("created_at"),
            updated_at=response.get("updated_at"),
        )

    except (BadRequestError, NotFoundError) as e:
        raise RuntimeError(f"Failed to get audience details: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error getting audience details: {e}")


def create_audience(app_id: str, attributes: dict) -> AudienceCreateMCPResponse:
    """
    Create a new audience using validated attributes.

    Args:
        app_id: UUID of the app to create audience for
        attributes: Dictionary containing audience attributes

    Returns:
        Dictionary with creation status and audience information

    Raises:
        RuntimeError: If validation fails or API request fails
    """
    try:
        client = create_piwik_client()

        # Validate attributes using Pydantic model
        validated_attrs = validate_data_against_model(attributes, NewAudienceAttributes)

        # Create audience using the API
        response = client.cdp.create_audience(
            app_id=app_id,
            name=validated_attrs.name,
            description=validated_attrs.description,
            definition=validated_attrs.definition.model_dump(mode="json", by_alias=True, exclude_none=True),
            membership_duration_days=validated_attrs.membership_duration_days,
        )

        if response:
            return AudienceCreateMCPResponse(
                status="success",
                message=f"Successfully created audience '{validated_attrs.name}'",
                audience_id=response.get("id"),
                audience_name=response.get("name"),
            )
        else:
            return AudienceCreateMCPResponse(
                status="success",
                message=f"Successfully created audience '{validated_attrs.name}'",
                audience_name=validated_attrs.name,
            )

    except (BadRequestError, NotFoundError) as e:
        raise RuntimeError(f"Failed to create audience: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error creating audience: {e}")


def update_audience(app_id: str, audience_id: str, attributes: dict) -> AudienceUpdateMCPResponse:
    """
    Update an existing audience using validated attributes.

    Args:
        app_id: UUID of the app containing the audience
        audience_id: UUID of the audience to update
        attributes: Dictionary containing audience attributes to update

    Returns:
        Dictionary with update status and audience information

    Raises:
        RuntimeError: If validation fails or API request fails
    """
    try:
        client = create_piwik_client()

        # First, get the current audience data since all fields are required for updates
        current_audience_response = client.cdp.get_audience(app_id=app_id, audience_id=audience_id)
        if not current_audience_response:
            raise RuntimeError(f"Audience {audience_id} not found")

        current_data = {
            "name": current_audience_response.get("name", ""),
            "description": current_audience_response.get("description", ""),
            "definition": current_audience_response.get("definition", {}),
            "membership_duration_days": current_audience_response.get("membership_duration_days", 30),
        }

        # Merge current data with provided attributes (attributes override current values)
        merged_attributes = {**current_data, **attributes}

        validated_attrs = validate_data_against_model(merged_attributes, EditableAudienceAttributes)

        # Track which fields were actually provided by the user
        updated_fields = list(attributes.keys())

        client.cdp.update_audience(
            app_id=app_id,
            audience_id=audience_id,
            name=validated_attrs.name,
            description=validated_attrs.description,
            definition=validated_attrs.definition.model_dump(mode="json", by_alias=True, exclude_none=True),
            membership_duration_days=validated_attrs.membership_duration_days,
        )

        return AudienceUpdateMCPResponse(
            status="success",
            message=f"Successfully updated audience '{validated_attrs.name}' (fields: {', '.join(updated_fields)})",
            audience_id=audience_id,
            audience_name=validated_attrs.name,
            updated_fields=updated_fields,
        )

    except (BadRequestError, NotFoundError) as e:
        raise RuntimeError(f"Failed to update audience: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error updating audience: {e}")


def delete_audience(app_id: str, audience_id: str) -> OperationStatusResponse:
    """
    Delete an existing audience.

    Args:
        app_id: UUID of the app containing the audience
        audience_id: UUID of the audience to delete

    Returns:
        Dictionary with deletion status and message

    Raises:
        RuntimeError: If audience not found or API request fails
    """
    try:
        client = create_piwik_client()

        # Delete the audience
        client.cdp.delete_audience(app_id=app_id, audience_id=audience_id)

        return OperationStatusResponse(
            status="success",
            message=f"Successfully deleted audience {audience_id}",
        )

    except NotFoundError:
        raise RuntimeError(f"Audience {audience_id} not found")
    except BadRequestError as e:
        raise RuntimeError(f"Failed to delete audience: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error deleting audience: {e}")
