"""
Common Pydantic models for Piwik PRO API data structures.
"""

from typing import Any

from pydantic import BaseModel, Field


class JsonApiResource(BaseModel):
    """JSON API resource object."""

    type: str = Field(..., description="Resource type")
    id: str = Field(..., description="Resource ID")
    attributes: dict[str, Any] = Field(..., description="Resource attributes")


class JsonApiData(BaseModel):
    """JSON API data wrapper."""

    data: JsonApiResource | list[JsonApiResource]


class Meta(BaseModel):
    """Metadata for paginated responses."""

    total: int = Field(..., description="Total count of objects")


class ErrorDetail(BaseModel):
    """API error detail."""

    status: str = Field(..., description="HTTP status code")
    code: str | None = Field(None, description="Application-specific error code")
    title: str = Field(..., description="Error title")
    detail: str | None = Field(None, description="Error detail")
    source: dict[str, str] | None = Field(None, description="Error source")


class ErrorResponse(BaseModel):
    """API error response."""

    errors: list[ErrorDetail] = Field(..., description="List of errors")
