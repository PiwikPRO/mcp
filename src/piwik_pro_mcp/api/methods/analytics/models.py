"""
Pydantic models for Analytics Annotations responses.
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from ..common import Meta


class AnnotationAuthor(BaseModel):
    """Annotation author info (present for user annotations)."""

    email: str = Field(..., description="Email address of the author")


class UserAnnotationAttributes(BaseModel):
    """Attributes for a user annotation (JSON:API)."""

    date: str = Field(..., description="Annotation date (YYYY-MM-DD)")
    content: str = Field(..., description="Annotation content")
    visibility: Optional[str] = Field(None, description='"private" or "public"')
    website_id: Optional[str] = Field(None, description="App UUID associated with the annotation")
    author: Optional[AnnotationAuthor] = Field(None, description="Author info")
    is_author: Optional[bool] = Field(None, description="Whether current user is the author")


class SystemAnnotationAttributes(BaseModel):
    """Attributes for a system annotation (JSON:API)."""

    date: str = Field(..., description="Annotation date (YYYY-MM-DD)")
    content: str = Field(..., description="Annotation content")


class UserAnnotationResource(BaseModel):
    """User annotation resource."""

    id: str = Field(..., description="Annotation UUID")
    type: Literal["UserAnnotation"]
    attributes: UserAnnotationAttributes


class SystemAnnotationResource(BaseModel):
    """System annotation resource."""

    id: str = Field(..., description="Annotation UUID")
    type: Literal["SystemAnnotation"]
    attributes: SystemAnnotationAttributes


class UserAnnotationSingleResponse(BaseModel):
    """
    Response model for single annotation (user or system).
    """

    data: UserAnnotationResource = Field(..., description="User annotation resource")


class SystemAnnotationListResponse(BaseModel):
    """
    Response model for system annotations list endpoints.
    """

    data: List[SystemAnnotationResource] = Field(..., description="List of system annotation resources")
    meta: Meta = Field(..., description="Pagination metadata with total count")


class UserAnnotationListResponse(BaseModel):
    """
    Response model for user annotations list endpoints.
    """

    data: List[UserAnnotationResource] = Field(..., description="List of user annotation resources")
    meta: Meta = Field(..., description="Pagination metadata with total count")
