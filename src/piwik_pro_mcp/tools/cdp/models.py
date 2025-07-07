"""
MCP-specific models for CDP management tools.

This module provides Pydantic models used specifically by the MCP CDP tools
for validation and schema generation. Most CDP models are imported from
the piwik_pro_api.api.cdp.models module.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AudienceSummary(BaseModel):
    """Audience summary for list responses that matches MCP tool documentation."""

    id: str = Field(..., description="Audience UUID")
    name: str = Field(..., description="Audience name")
    description: str = Field(..., description="Audience description")
    membership_duration_days: int = Field(..., description="Membership duration in days")
    version: int = Field(..., description="Audience version")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    is_author: bool = Field(..., description="Whether current user is the author")


class AudienceListMCPResponse(BaseModel):
    """MCP-specific audience list response that matches documented schema."""

    audiences: List[AudienceSummary] = Field(..., description="List of audiences")
    total: int = Field(..., description="Total number of audiences available")


class AudienceDetailsMCPResponse(BaseModel):
    """MCP-specific audience details response."""

    id: str = Field(..., description="Audience UUID")
    name: str = Field(..., description="Audience name")
    description: str = Field(..., description="Audience description")
    membership_duration_days: int = Field(..., description="Membership duration in days")
    version: int = Field(..., description="Audience version")
    definition: Dict[str, Any] = Field(..., description="Audience definition with conditions")
    author_email: str = Field(..., description="Email of the audience author")
    is_author: bool = Field(..., description="Whether current user is the author")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class AudienceCreateMCPResponse(BaseModel):
    """MCP-specific audience creation response."""

    status: str = Field(..., description="Creation status (success, error)")
    message: str = Field(..., description="Descriptive message about the creation")
    audience_id: Optional[str] = Field(None, description="ID of the created audience")
    audience_name: Optional[str] = Field(None, description="Name of the created audience")


class AudienceUpdateMCPResponse(BaseModel):
    """MCP-specific audience update response."""

    status: str = Field(..., description="Update status (success, error)")
    message: str = Field(..., description="Descriptive message about the update")
    audience_id: Optional[str] = Field(None, description="ID of the updated audience")
    audience_name: Optional[str] = Field(None, description="Name of the updated audience")
    updated_fields: List[str] = Field(default_factory=list, description="List of fields that were updated")


class AttributeSummary(BaseModel):
    """Summary information about a CDP attribute for audience creation."""

    column_id: str = Field(..., description="Unique attribute identifier")
    event_data_key: str = Field(..., description="Key for imported data or tracker event dimension")
    immutable: bool = Field(..., description="Whether the attribute is read-only")
    column_name: str = Field(..., description="Human-readable attribute name")
    column_type: str = Field(..., description="Data type (string, number, datetime, etc.)")
    column_category: List[str] = Field(..., description="Categories the attribute belongs to")
    value_selectors: List[str] = Field(..., description="Supported value selectors (first, last, any)")
    scope: str = Field(..., description="Scope of the attribute (event or profile)")
    column_unit: Optional[str] = Field(None, description="Unit of measurement")
    supported_operators: List[str] = Field(
        default_factory=list, description="Supported filtering operators for this column type"
    )
    value_format: Dict[str, Any] = Field(
        default_factory=dict, description="Value format requirements and examples for this column type"
    )


class AttributeListMCPResponse(BaseModel):
    """MCP-specific response for listing CDP attributes."""

    attributes: List[AttributeSummary] = Field(..., description="List of CDP attributes with metadata")
    total: int = Field(..., description="Total number of attributes available")
