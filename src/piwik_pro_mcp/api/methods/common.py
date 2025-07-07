"""
Common Pydantic models for Piwik PRO API data structures.
"""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class JsonApiResource(BaseModel):
    """JSON API resource object."""

    type: str = Field(..., description="Resource type")
    id: str = Field(..., description="Resource ID")
    attributes: Dict[str, Any] = Field(..., description="Resource attributes")


class JsonApiData(BaseModel):
    """JSON API data wrapper."""

    data: Union[JsonApiResource, List[JsonApiResource]]


class Meta(BaseModel):
    """Metadata for paginated responses."""

    total: int = Field(..., description="Total count of objects")


class ErrorDetail(BaseModel):
    """API error detail."""

    status: str = Field(..., description="HTTP status code")
    code: Optional[str] = Field(None, description="Application-specific error code")
    title: str = Field(..., description="Error title")
    detail: Optional[str] = Field(None, description="Error detail")
    source: Optional[Dict[str, str]] = Field(None, description="Error source")


class ErrorResponse(BaseModel):
    """API error response."""

    errors: List[ErrorDetail] = Field(..., description="List of errors")
