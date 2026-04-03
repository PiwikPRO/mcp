"""Pydantic models for Piwik PRO Tracker Settings API data structures."""

from enum import Enum

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


class TrackerSettingsBase(BaseModel):
    """Shared tracker settings fields exposed by the v2 API."""

    model_config = ConfigDict(populate_by_name=True)

    anonymize_visitor_geolocation_level: GeolocationLevel | None = Field(
        None, description="Removes geolocation data more granular than the selected level"
    )
    anonymize_visitor_ip_level: int | None = Field(
        None, ge=0, le=4, description="Anonymize 'n' octets of visitor IP addresses"
    )
    campaign_content_params: list[str] | None = Field(
        None, description="URL parameters used to identify campaign content"
    )
    campaign_id_params: list[str] | None = Field(None, description="URL parameters used to identify the campaign ID")
    campaign_keyword_params: list[str] | None = Field(
        None, description="URL parameters used to identify campaign keywords"
    )
    campaign_medium_params: list[str] | None = Field(
        None, description="URL parameters used to identify the campaign medium"
    )
    campaign_name_params: list[str] | None = Field(
        None, description="URL parameters used to identify the campaign name"
    )
    campaign_source_params: list[str] | None = Field(
        None, description="URL parameters used to identify the campaign source"
    )
    create_new_visit_when_campaign_changes: bool | None = Field(
        None, description="If true, starts a new session when the campaign name or type changes"
    )
    create_new_visit_when_website_referrer_changes: bool | None = Field(
        None, description="If true, starts a new session when the referrer name or type changes"
    )
    enable_fingerprinting_across_websites: bool | None = Field(
        None, description="If true, tries to generate a unified visitor ID across different websites"
    )
    set_ip_tracking: bool | None = Field(
        None, description="If false, tracker will remove all IP information from the request"
    )
    exclude_crawlers: bool | None = Field(None, description="If true, crawler bots are not tracked")
    exclude_unknown_urls: bool | None = Field(
        None, description="If true, requests from URLs not listed in the urls collection are discarded"
    )
    excluded_ips: list[str] | None = Field(None, description="A list of IPs to blacklist from tracking")
    excluded_user_agents: list[str] | None = Field(
        None, description="A list of user agent strings to exclude from tracking"
    )
    fingerprint_based_on_anonymized_ip: bool | None = Field(
        None, description="If true, geolocation is based on the anonymized IP"
    )
    keep_url_fragment: bool | None = Field(
        None, description="If false, the URL fragment (part after '#') is removed before tracking"
    )
    session_limit_exceeded_action: SessionLimitAction | None = Field(
        None, description="Defines behavior when a session limit is reached"
    )
    session_max_duration_seconds: int | None = Field(
        None, ge=1, le=43200, description="The maximum duration of a session in seconds"
    )
    session_max_event_count: int | None = Field(
        None, ge=1, le=65535, description="The maximum number of events in a session"
    )
    site_search_category_params: list[str] | None = Field(
        None, description="URL parameters used for site search categories"
    )
    site_search_query_params: list[str] | None = Field(None, description="URL parameters used for site search keywords")
    strip_site_search_query_parameters: bool | None = Field(
        None, description="If true, site search parameters are removed from URLs in reports"
    )
    tracking_fingerprint_disabled: bool | None = Field(
        None, description="If true, the tracker will use the fingerprint from the cookie"
    )
    use_session_hash: bool | None = Field(
        None, description="If true, non-anonymous events are matched into sessions using a Session Hash"
    )
    use_anonymous_session_hash: bool | None = Field(
        None, description="If true, anonymous events are matched into sessions using a Session Hash"
    )
    url_query_parameter_to_exclude_from_url: list[str] | None = Field(
        None, description="A list of URL query parameters to exclude from tracking"
    )
    updated_at: str | None = Field(None, description="Timestamp of the object's last modification")


class GlobalTrackerSettings(TrackerSettingsBase):
    """Global tracker settings model."""


class AppTrackerSettings(TrackerSettingsBase):
    """App-specific tracker settings model."""

    urls: list[str] | None = Field(None, description="A list of valid URLs for the app")
