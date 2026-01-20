"""
MCP-specific models for Tag Manager tools.

This module provides Pydantic models used specifically by the MCP Tag Manager tools
for validation and schema generation.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator

from ...common.settings import tag_manager_resource_check_enabled
from ...common.templates import list_template_names


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
        allowed = set(list_template_names("tag_manager/tags"))
        if v not in allowed:
            raise ValueError(f"Unsupported tag template '{v}'. Use templates_list() to discover options.")
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

    name: str = Field(..., description="Variable name")
    variable_type: str = Field(..., description="Variable type")
    is_active: Optional[bool] = Field(None, description="Whether variable is active")

    # Data Layer variable fields
    data_layer_variable_name: Optional[str] = Field(None, description="Data layer property name to access")
    data_layer_version: Optional[str] = Field(None, description="Data layer version (1 or 2)")
    default_value: Optional[str] = Field(None, description="Fallback value when property is undefined")
    decode_uri_component: Optional[bool] = Field(None, description="Whether to decode URI components")
    # Custom JavaScript variable fields
    code: Optional[str] = Field(None, description="JavaScript code to execute")
    # Constant variable fields
    value: Optional[str] = Field(None, description="Constant value for constant variables")
    # URL variable fields
    url_component: Optional[str] = Field(None, description="URL component to extract (host, path, query, etc.)")
    # Cookie variable fields
    cookie_name: Optional[str] = Field(None, description="Name of cookie to read")
    # Random number variable fields
    min_value: Optional[int] = Field(None, description="Minimum value for random number")
    max_value: Optional[int] = Field(None, description="Maximum value for random number")

    @field_validator("variable_type")
    @classmethod
    def _validate_variable_type(cls, v: str) -> str:
        if not tag_manager_resource_check_enabled():
            return v
        allowed = set(list_template_names("tag_manager/variables"))
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
        allowed = set(list_template_names("tag_manager/triggers"))
        if v not in allowed:
            raise ValueError(f"Unsupported trigger type '{v}'. Use templates_list_triggers() to discover options.")
        return v


class VariableUpdateAttributes(BaseModel):
    """Attributes for updating variables with template-specific fields."""

    model_config = {"extra": "allow"}  # Allow additional fields for template-specific attributes

    name: Optional[str] = Field(None, description="Variable name")
    is_active: Optional[bool] = Field(None, description="Whether variable is active")

    # Data Layer variable fields
    data_layer_variable_name: Optional[str] = Field(None, description="Data layer property name to access")
    data_layer_version: Optional[str] = Field(None, description="Data layer version (1 or 2)")
    default_value: Optional[str] = Field(None, description="Fallback value when property is undefined")
    decode_uri_component: Optional[bool] = Field(None, description="Whether to decode URI components")
    # Custom JavaScript variable fields
    code: Optional[str] = Field(None, description="JavaScript code to execute")

    # Constant variable fields
    value: Optional[str] = Field(None, description="Constant value for constant variables")

    # DOM Element variable fields
    element_selector: Optional[str] = Field(None, description="CSS selector or XPath to identify target element")
    selection_method: Optional[str] = Field(None, description="Selection method: 'css' or 'xpath'")
    attribute_name: Optional[str] = Field(None, description="HTML attribute to extract (empty for text content)")

    # URL variable fields
    url_component: Optional[str] = Field(None, description="URL component to extract (host, path, query, etc.)")
    # Cookie variable fields
    cookie_name: Optional[str] = Field(None, description="Name of cookie to read")
    # Random number variable fields
    min_value: Optional[int] = Field(None, description="Minimum value for random number")
    max_value: Optional[int] = Field(None, description="Maximum value for random number")


class PublishStatusResponse(BaseModel):
    """Response for version publishing operations."""

    status: str = Field(..., description="Operation status")
    message: str = Field(..., description="Operation details")
    version_info: Dict[str, Any] = Field(default_factory=dict, description="Information about the published version")
