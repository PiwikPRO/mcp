"""
MCP-specific models for tracker settings tools.

This module provides Pydantic models used specifically by the MCP tracker settings tools
for validation and schema generation. Most tracker settings models are imported from
the piwik_pro_api.api.tracker_settings.models module.
"""

from typing import Optional

from pydantic import BaseModel, Field


class TrackerSettingsUpdateRequest(BaseModel):
    """MCP-specific model for tracker settings update requests."""

    model_config = {"extra": "forbid"}

    # Common tracker settings that can be updated
    anonymize_visitor_ip_level: Optional[int] = Field(None, description="IP anonymization level (0-4)")
    excluded_ips: Optional[list[str]] = Field(None, description="List of IPs excluded from tracking")
    excluded_url_params: Optional[list[str]] = Field(None, description="URL parameters excluded from tracking")
    excluded_user_agents: Optional[list[str]] = Field(None, description="User agents excluded from tracking")
    site_search_query_params: Optional[list[str]] = Field(None, description="Site search query parameters")
    site_search_category_params: Optional[list[str]] = Field(None, description="Site search category parameters")
    exclude_crawlers: Optional[bool] = Field(None, description="Whether to exclude crawlers")

    # App-specific settings (available for app tracker settings)
    session_max_duration_seconds: Optional[int] = Field(None, description="Maximum session duration in seconds")
    campaign_name_params: Optional[list[str]] = Field(None, description="Campaign name parameters")
    campaign_keyword_params: Optional[list[str]] = Field(None, description="Campaign keyword parameters")
    campaign_source_params: Optional[list[str]] = Field(None, description="Campaign source parameters")
    campaign_medium_params: Optional[list[str]] = Field(None, description="Campaign medium parameters")
    campaign_content_params: Optional[list[str]] = Field(None, description="Campaign content parameters")
    campaign_id_params: Optional[list[str]] = Field(None, description="Campaign ID parameters")
