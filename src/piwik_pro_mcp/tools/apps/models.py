"""
MCP-specific models for app management tools.

This module provides Pydantic models used specifically by the MCP app tools
for validation and schema generation. Most app models are imported from
the API methods app models module.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class AppSummary(BaseModel):
    """App summary for list responses that matches MCP tool documentation."""

    id: str = Field(..., description="App UUID")
    name: str = Field(..., description="App name")
    created_at: datetime | None = Field(None, description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")


class AppListMCPResponse(BaseModel):
    """MCP-specific app list response that matches documented schema."""

    apps: list[AppSummary] = Field(..., description="List of app objects with id, name, urls, timezone, currency, etc.")
    total: int = Field(..., description="Total number of apps available")
    limit: int = Field(..., description="Number of apps requested")
    offset: int = Field(..., description="Number of apps skipped")


class AppDetailsMCPResponse(BaseModel):
    """MCP-specific app details response that matches documented schema."""

    id: str = Field(..., description="App UUID")
    name: str = Field(..., description="App name")
    urls: list[str] = Field(..., description="List of URLs where the app is available")
    app_type: str | None = Field(None, description="Type of application")
    timezone: str | None = Field(None, description="App timezone")
    currency: str | None = Field(None, description="App currency")
    e_commerce_tracking: bool | None = Field(None, description="Whether e-commerce tracking is enabled")
    delay: int | None = Field(None, description="App delay in milliseconds")
    gdpr_enabled: bool | None = Field(None, description="Whether GDPR is enabled")
    gdpr_user_mode_enabled: bool | None = Field(None, description="Whether GDPR user mode is enabled")
    privacy_cookie_domains_enabled: bool | None = Field(
        None,
        description="Whether privacy cookie domains are enabled",
    )
    privacy_cookie_expiration_period: int | None = Field(
        None,
        description="Privacy cookie expiration period in seconds",
    )
    privacy_cookie_domains: list[str] | None = Field(None, description="List of privacy cookie domains")
    gdpr_data_anonymization: bool | None = Field(None, description="GDPR data anonymization setting")
    sharepoint_integration: bool | None = Field(None, description="Whether SharePoint integration is enabled")
    gdpr_data_anonymization_mode: str | None = Field(None, description="GDPR data anonymization mode")
    privacy_use_cookies: bool | None = Field(None, description="Whether privacy mode uses cookies")
    privacy_use_fingerprinting: bool | None = Field(
        None,
        description="Whether privacy mode uses fingerprinting",
    )
    cnil: bool | None = Field(None, description="Whether CNIL integration is enabled")
    session_id_strict_privacy_mode: bool | None = Field(
        None,
        description="Whether session ID strict privacy mode is enabled",
    )
    real_time_dashboards: bool | None = Field(None, description="Real-time dashboards enabled")
    created_at: datetime | None = Field(None, description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")


class AppCreateMCPResponse(BaseModel):
    """MCP-specific app creation response that matches documented schema."""

    id: str = Field(..., description="Generated app UUID")
    name: str = Field(..., description="App name")
    urls: list[str] = Field(..., description="List of URLs")
    timezone: str | None = Field(None, description="App timezone")
    currency: str | None = Field(None, description="App currency")
    gdpr_enabled: bool | None = Field(None, description="GDPR status")
    created_at: datetime | None = Field(None, description="Creation timestamp")
