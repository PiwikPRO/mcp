"""
Pydantic models for Piwik PRO Tracker Settings API data structures.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class GeolocationLevel(str, Enum):
    """Geolocation anonymization level enumeration."""

    NONE = "none"
    CITY = "City"
    REGION = "Region"
    COUNTRY = "Country"
    CONTINENT = "Continent"


class SessionLimitAction(str, Enum):
    """Session limit exceeded action enumeration."""

    SPLIT_AND_EXCLUDE = "split_and_exclude"
    JUST_SPLIT = "just_split"


class GlobalTrackerSettings(BaseModel):
    """Global tracker settings model."""

    model_config = ConfigDict(populate_by_name=True)

    anonymize_visitor_ip_level: Optional[int] = Field(
        None, ge=0, le=3, description="Anonymize 'n' octets of Visitors IP addresses"
    )
    excluded_ips: Optional[List[str]] = Field(
        None, description="List of IPs to blacklist from tracking. You can use wildcards"
    )
    excluded_url_params: Optional[List[str]] = Field(
        None, description="URL query parameters excluded by default from tracking"
    )
    excluded_user_agents: Optional[List[str]] = Field(None, description="User agent strings to exclude from tracking")
    site_search_query_params: Optional[List[str]] = Field(None, description="Site search query params for an app")
    site_search_category_params: Optional[List[str]] = Field(None, description="Site search category params for an app")
    visitor_geolocation_based_on_anonymized_ip: Optional[bool] = Field(
        None, description="When set, visitor geolocation calculation is based on an anonymized IP"
    )
    updated_at: Optional[str] = Field(None, description="Timestamp of object's last modification")


class AppTrackerSettings(BaseModel):
    """App-specific tracker settings model."""

    model_config = ConfigDict(populate_by_name=True)

    anonymize_visitor_geolocation_level: Optional[GeolocationLevel] = Field(
        None, description="Removes geolocation data more granular than the selected level"
    )
    anonymize_visitor_ip_level: Optional[int] = Field(
        None, ge=0, le=4, description="Anonymizes 'n' octets of visitor IP addresses"
    )
    campaign_content_params: Optional[List[str]] = Field(
        None, description="URL parameters used to identify campaign content"
    )
    campaign_id_params: Optional[List[str]] = Field(None, description="URL parameters used to identify the campaign ID")
    campaign_keyword_params: Optional[List[str]] = Field(
        None, description="URL parameters used to identify campaign keywords"
    )
    campaign_medium_params: Optional[List[str]] = Field(
        None, description="URL parameters used to identify the campaign medium"
    )
    campaign_name_params: Optional[List[str]] = Field(
        None, description="URL parameters used to identify the campaign name"
    )
    campaign_source_params: Optional[List[str]] = Field(
        None, description="URL parameters used to identify the campaign source"
    )
    create_new_visit_when_campaign_changes: Optional[bool] = Field(
        None, description="If true, starts a new session when the campaign name or type changes"
    )
    create_new_visit_when_website_referrer_changes: Optional[bool] = Field(
        None, description="If true, starts a new session when the referrer name or type changes"
    )
    enable_fingerprinting_across_websites: Optional[bool] = Field(
        None, description="If true, tries to generate a unified visitor ID across different websites"
    )
    set_ip_tracking: Optional[bool] = Field(
        None, description="If false, tracker will remove all IP information from the request"
    )
    exclude_crawlers: Optional[bool] = Field(None, description="If true, crawler bots are not tracked")
    exclude_unknown_urls: Optional[bool] = Field(
        None, description="If true, requests from URLs not listed in the urls collection are discarded"
    )
    excluded_ips: Optional[List[str]] = Field(None, description="A list of IPs to blacklist from tracking")
    excluded_user_agents: Optional[List[str]] = Field(
        None, description="A list of user agent strings to exclude from tracking"
    )
    fingerprint_based_on_anonymized_ip: Optional[bool] = Field(
        None, description="If true, geolocation is based on the anonymized IP"
    )
    keep_url_fragment: Optional[bool] = Field(
        None, description="If false, the URL fragment (part after '#') is removed before tracking"
    )
    session_limit_exceeded_action: Optional[SessionLimitAction] = Field(
        None, description="Defines behavior when a session limit is reached"
    )
    session_max_duration_seconds: Optional[int] = Field(
        None, ge=1, le=43200, description="The maximum duration of a session in seconds"
    )
    session_max_event_count: Optional[int] = Field(
        None, ge=1, le=65535, description="The maximum number of events in a session"
    )
    site_search_category_params: Optional[List[str]] = Field(
        None, description="URL parameters used for site search categories"
    )
    site_search_query_params: Optional[List[str]] = Field(
        None, description="URL parameters used for site search keywords"
    )
    strip_site_search_query_parameters: Optional[bool] = Field(
        None, description="If true, site search parameters are removed from URLs in reports"
    )
    tracking_fingerprint_disabled: Optional[bool] = Field(
        None, description="If true, the tracker will use the fingerprint from the cookie"
    )
    use_session_hash: Optional[bool] = Field(
        None, description="If true, non-anonymous events are matched into sessions using a Session Hash"
    )
    use_anonymous_session_hash: Optional[bool] = Field(
        None, description="If true, anonymous events are matched into sessions using a Session Hash"
    )
    url_query_parameter_to_exclude_from_url: Optional[List[str]] = Field(
        None, description="A list of URL query parameters to exclude from tracking"
    )
    urls: Optional[List[str]] = Field(None, description="A list of valid URLs for the app")
    updated_at: Optional[str] = Field(None, description="Timestamp of the object's last modification")
