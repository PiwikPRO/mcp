"""
Pydantic models for MCP Analytics Annotation tool responses.
"""

from typing import Any, Dict, List, Union

from pydantic import BaseModel, Field

from piwik_pro_mcp.api.methods.analytics.models import SystemAnnotationResource, UserAnnotationResource

AnnotationResource = Union[UserAnnotationResource, SystemAnnotationResource]


class AnnotationsList(BaseModel):
    """Combined list output for annotations_list tool."""

    data: List[AnnotationResource] = Field(..., description="List of annotations")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Metadata such as total count")


class AnnotationItem(BaseModel):
    """Single annotation output for create/get/update tools."""

    data: AnnotationResource
