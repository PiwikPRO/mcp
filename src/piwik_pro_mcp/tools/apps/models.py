"""
MCP-specific models for app management tools.

This module provides Pydantic models used specifically by the MCP app tools
for validation and schema generation. Most app models are imported from
the piwik_pro_api.api.apps.models module.
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
    gdpr_enabled: bool | None = Field(None, description="Whether GDPR is enabled")
    gdpr_data_anonymization: bool | None = Field(None, description="GDPR data anonymization setting")
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
