"""
MCP-specific models for Tag Manager tools.

This module provides Pydantic models used specifically by the MCP Tag Manager tools
for validation and schema generation.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator

from ...common.settings import tag_manager_resource_check_enabled
from ...common.templates import list_available_assets


class TagManagerCreateAttributes(BaseModel):
    """Base attributes for creating Tag Manager resources."""

    model_config = {"extra": "allow"}  # Allow additional fields for template-specific attributes

    name: str = Field(..., description="Resource name")
    template: str = Field(..., description="Resource template")
    is_active: Optional[bool] = Field(None, description="Whether resource is active")

    # Common template-specific fields that many templates use
    code: Optional[str] = Field(None, description="Tag code (HTML, script, or CSS)")
    consent_type: Optional[str] = Field(None, description="Consent type for privacy compliance")
    tag_type: Optional[str] = Field(None, description="Tag execution type (sync/async)")
    document_write: Optional[bool] = Field(None, description="Whether tag uses document.write")
    disable_in_debug_mode: Optional[bool] = Field(None, description="Disable in debug mode")
    respect_visitors_privacy: Optional[bool] = Field(None, description="Respect visitor privacy settings")
    priority: Optional[int] = Field(None, description="Tag firing priority")
    template_options: Optional[Dict[str, Any]] = Field(None, description="Template-specific options")

    @field_validator("template")
    @classmethod
    def _validate_template(cls, v: str) -> str:
        if not tag_manager_resource_check_enabled():
            return v
        allowed = set(list_available_assets("tag_manager/tags").keys())
        if v not in allowed:
            raise ValueError(f"Unsupported tag template '{v}'. Use templates_list_tags() to discover options.")
        return v


class TagManagerUpdateAttributes(BaseModel):
    """Base attributes for updating Tag Manager resources."""

    model_config = {"extra": "allow"}  # Allow additional fields for template-specific attributes

    name: Optional[str] = Field(None, description="Resource name")
    template: Optional[str] = Field(None, description="Resource template")
    is_active: Optional[bool] = Field(None, description="Whether resource is active")

    # Common template-specific fields that many templates use
    code: Optional[str] = Field(None, description="Tag code (HTML, script, or CSS)")
    consent_type: Optional[str] = Field(None, description="Consent type for privacy compliance")
    tag_type: Optional[str] = Field(None, description="Tag execution type (sync/async)")
    document_write: Optional[bool] = Field(None, description="Whether tag uses document.write")
    disable_in_debug_mode: Optional[bool] = Field(None, description="Disable in debug mode")
    respect_visitors_privacy: Optional[bool] = Field(None, description="Respect visitor privacy settings")
    priority: Optional[int] = Field(None, description="Tag firing priority")
    template_options: Optional[Dict[str, Any]] = Field(None, description="Template-specific options")


class VariableCreateAttributes(BaseModel):
    """Attributes for creating variables with template-specific fields."""

    model_config = {"extra": "allow"}  # Allow additional fields for template-specific attributes

    variable_type: str = Field(..., description="Variable type")
    name: str = Field(..., description="Variable name")
    is_active: Optional[bool] = Field(None, description="Whether variable is active")
    value: Optional[str] = Field(None, description="Value differs based on variable type")
    options: Optional[Dict[str, Any]] = Field(None, description="Template-specific options.")

    @field_validator("variable_type")
    @classmethod
    def _validate_variable_type(cls, v: str) -> str:
        if not tag_manager_resource_check_enabled():
            return v
        allowed = set(list_available_assets("tag_manager/variables").keys())
        if v not in allowed:
            raise ValueError(f"Unsupported variable type '{v}'. Use templates_list_variables() to discover options.")
        return v


class TriggerCreateAttributes(BaseModel):
    """Attributes for creating triggers with assets-based allowlist enforcement."""

    model_config = {"extra": "allow"}

    name: str = Field(..., description="Trigger name")
    trigger_type: str = Field(..., description="Trigger type (must match assets)")
    is_active: Optional[bool] = Field(None, description="Whether trigger is active")

    @field_validator("trigger_type")
    @classmethod
    def _validate_trigger_type(cls, v: str) -> str:
        if not tag_manager_resource_check_enabled():
            return v
        allowed = set(list_available_assets("tag_manager/triggers").keys())
        if v not in allowed:
            raise ValueError(f"Unsupported trigger type '{v}'. Use templates_list_triggers() to discover options.")
        return v


class VariableUpdateAttributes(BaseModel):
    """Attributes for updating variables with template-specific fields."""

    model_config = {"extra": "allow"}  # Allow additional fields for template-specific attributes

    name: Optional[str] = Field(None, description="Variable name")
    is_active: Optional[bool] = Field(None, description="Whether variable is active")
    value: Optional[str] = Field(None, description="Value differs based on variable type")
    options: Optional[Dict[str, Any]] = Field(None, description="Template-specific options.")


class PublishStatusResponse(BaseModel):
    """Response for version publishing operations."""

    status: str = Field(..., description="Operation status")
    message: str = Field(..., description="Operation details")
    version_info: Dict[str, Any] = Field(default_factory=dict, description="Information about the published version")
