"""
MCP-specific models for tracker settings tools.

This module provides Pydantic models used specifically by the MCP tracker settings tools
for validation and schema generation. Most tracker settings models are imported from
the piwik_pro_api.api.tracker_settings.models module.
"""

from pydantic import BaseModel, Field


class TrackerSettingsUpdateRequest(BaseModel):
    """MCP-specific model for tracker settings update requests."""

    model_config = {"extra": "forbid"}

    # Common tracker settings that can be updated
    anonymize_visitor_ip_level: int | None = Field(None, description="IP anonymization level (0-4)")
    excluded_ips: list[str] | None = Field(None, description="List of IPs excluded from tracking")
    excluded_url_params: list[str] | None = Field(None, description="URL parameters excluded from tracking")
    excluded_user_agents: list[str] | None = Field(None, description="User agents excluded from tracking")
    site_search_query_params: list[str] | None = Field(None, description="Site search query parameters")
    site_search_category_params: list[str] | None = Field(None, description="Site search category parameters")
    exclude_crawlers: bool | None = Field(None, description="Whether to exclude crawlers")

    # App-specific settings (available for app tracker settings)
    session_max_duration_seconds: int | None = Field(None, description="Maximum session duration in seconds")
    campaign_name_params: list[str] | None = Field(None, description="Campaign name parameters")
    campaign_keyword_params: list[str] | None = Field(None, description="Campaign keyword parameters")
    campaign_source_params: list[str] | None = Field(None, description="Campaign source parameters")
    campaign_medium_params: list[str] | None = Field(None, description="Campaign medium parameters")
    campaign_content_params: list[str] | None = Field(None, description="Campaign content parameters")
    campaign_id_params: list[str] | None = Field(None, description="Campaign ID parameters")
