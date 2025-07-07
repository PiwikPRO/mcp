"""
Pydantic models for Container Settings API responses.
"""

from typing import List

from pydantic import BaseModel, Field

from ..common import JsonApiResource


class InstallationCodeResponse(BaseModel):
    """
    Response for installation code endpoint.

    Follows JSON:API structure and reuses common resource model.
    """

    data: JsonApiResource = Field(..., description="Installation code resource with attributes including 'code'")


class ContainerSettingsListResponse(BaseModel):
    """
    Response for container settings list endpoint.
    """

    data: List[JsonApiResource] = Field(..., description="List of settings resources")
