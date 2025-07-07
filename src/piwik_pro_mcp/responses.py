#!/usr/bin/env python3
"""
MCP-specific Response Models for Piwik PRO Analytics API

This module provides minimal Pydantic models for MCP-specific operations
like create/update/delete status responses. It complements the existing
piwik_pro_api models without duplicating API response structures.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class OperationStatusResponse(BaseModel):
    """Standard response for create/update/delete operations."""

    status: str = Field(..., description="Operation status (success, error, etc.)")
    message: str = Field(..., description="Descriptive message about the operation")


class UpdateStatusResponse(BaseModel):
    """Response for update operations with field tracking."""

    status: str = Field(..., description="Update status")
    message: str = Field(..., description="Descriptive message about the update")
    updated_fields: List[str] = Field(..., description="List of fields that were updated")


class TrackerSettingsResponse(BaseModel):
    """Response model for tracker settings (supports both global and app-specific)."""

    # Global tracker settings (V1) fields
    anonymize_visitor_ip_level: Optional[int] = Field(None, description="Anonymize 'n' octets of visitor IP addresses")
    excluded_ips: List[str] = Field(default_factory=list, description="IPs excluded from tracking")
    excluded_url_params: List[str] = Field(default_factory=list, description="URL parameters excluded from tracking")
    excluded_user_agents: List[str] = Field(
        default_factory=list, description="User agent strings excluded from tracking"
    )
    site_search_query_params: List[str] = Field(default_factory=list, description="Site search query parameters")
    site_search_category_params: List[str] = Field(default_factory=list, description="Site search category parameters")
    visitor_geolocation_based_on_anonymized_ip: Optional[bool] = Field(
        None, description="Visitor geolocation based on anonymized IP"
    )

    # App tracker settings (V2) fields
    anonymize_visitor_geolocation_level: Optional[str] = Field(None, description="Geolocation anonymization level")
    campaign_content_params: List[str] = Field(default_factory=list, description="Campaign content parameters")
    campaign_id_params: List[str] = Field(default_factory=list, description="Campaign ID parameters")
    campaign_keyword_params: List[str] = Field(default_factory=list, description="Campaign keyword parameters")
    campaign_medium_params: List[str] = Field(default_factory=list, description="Campaign medium parameters")
    campaign_name_params: List[str] = Field(default_factory=list, description="Campaign name parameters")
    campaign_source_params: List[str] = Field(default_factory=list, description="Campaign source parameters")
    create_new_visit_when_campaign_changes: Optional[bool] = Field(
        None, description="Create new visit when campaign changes"
    )
    create_new_visit_when_website_referrer_changes: Optional[bool] = Field(
        None, description="Create new visit when referrer changes"
    )
    enable_fingerprinting_across_websites: Optional[bool] = Field(
        None, description="Enable fingerprinting across websites"
    )
    set_ip_tracking: Optional[bool] = Field(None, description="Enable IP tracking")
    exclude_crawlers: Optional[bool] = Field(None, description="Exclude crawler bots")
    exclude_unknown_urls: Optional[bool] = Field(None, description="Exclude unknown URLs")
    fingerprint_based_on_anonymized_ip: Optional[bool] = Field(None, description="Fingerprint based on anonymized IP")
    keep_url_fragment: Optional[bool] = Field(None, description="Keep URL fragment in tracking")
    session_limit_exceeded_action: Optional[str] = Field(None, description="Session limit exceeded action")
    session_max_duration_seconds: Optional[int] = Field(None, description="Maximum session duration in seconds")
    session_max_event_count: Optional[int] = Field(None, description="Maximum events per session")
    strip_site_search_query_parameters: Optional[bool] = Field(None, description="Strip site search query parameters")
    tracking_fingerprint_disabled: Optional[bool] = Field(None, description="Disable tracking fingerprint")
    use_session_hash: Optional[bool] = Field(None, description="Use session hash for non-anonymous events")
    use_anonymous_session_hash: Optional[bool] = Field(None, description="Use session hash for anonymous events")
    url_query_parameter_to_exclude_from_url: List[str] = Field(
        default_factory=list, description="URL query parameters to exclude"
    )
    urls: List[str] = Field(default_factory=list, description="Valid URLs for the app")

    # Common field
    updated_at: Optional[str] = Field(None, description="Last modification timestamp")


class InstallationCodeMCPResponse(BaseModel):
    """Response model for container installation code tool."""

    code: str = Field("", description="Installation code snippet")


class CopyResourceResponse(BaseModel):
    """
    Normalized response for Tag Manager copy operations.

    Provides a consistent shape across tags, triggers, and variables, abstracting
    minor schema differences in API responses.

    Attributes:
        resource_id: UUID of the newly created resource copy
        resource_type: Resource type (tag | trigger | variable)
        operation_id: UUID of the background operation created by the copy call
        copied_into_app_id: App UUID where the copy was created
        name: Optional new name of the copied resource, when available
        with_triggers: Indicates whether triggers were copied (tags only)
    """

    resource_id: str = Field(..., description="UUID of the copied resource")
    resource_type: str = Field(..., description="Resource type")
    operation_id: str = Field(..., description="Operation UUID created by the copy call")
    copied_into_app_id: str = Field(..., description="Target app UUID")
    name: Optional[str] = Field(None, description="Name of the copied resource if available")
    with_triggers: Optional[bool] = Field(None, description="Whether triggers were copied (tags only)")
