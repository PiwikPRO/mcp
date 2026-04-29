"""
Pydantic models for Piwik PRO Apps API data structures.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from ..common import JsonApiResource, Meta


class AppType(str, Enum):
    """App type enumeration."""

    WEB = "web"
    SHAREPOINT = "sharepoint"
    DEMO = "demo"


class Permission(str, Enum):
    """Permission enumeration."""

    VIEW = "view"
    EDIT = "edit"
    PUBLISH = "publish"
    MANAGE = "manage"


class SortOrder(str, Enum):
    """Sort order enumeration."""

    NAME = "name"
    ADDED_AT = "addedAt"
    UPDATED_AT = "updatedAt"
    NAME_DESC = "-name"
    ADDED_AT_DESC = "-addedAt"
    UPDATED_AT_DESC = "-updatedAt"


class GdprDataAnonymizationMode(str, Enum):
    """GDPR data anonymization mode."""

    NO_DEVICE_STORAGE = "no_device_storage"
    SESSION_COOKIE_ID = "session_cookie_id"


class AppEditableAttributes(BaseModel):
    """Editable attributes of an app."""

    model_config = ConfigDict(populate_by_name=True)

    name: str | None = Field(None, max_length=90, description="App name")
    urls: list[str] | None = Field(None, description="List of URLs under which the app is available")
    timezone: str | None = Field(None, description="App timezone (IANA format)")
    currency: str | None = Field(None, description="App currency")
    e_commerce_tracking: bool | None = Field(None, alias="eCommerceTracking")
    delay: int | None = Field(None, description="Delay in ms")
    gdpr: bool | None = Field(None, description="Enable GDPR compliance")
    gdpr_user_mode_enabled: bool | None = Field(None, alias="gdprUserModeEnabled")
    privacy_cookie_domains_enabled: bool | None = Field(None, alias="privacyCookieDomainsEnabled")
    privacy_cookie_expiration_period: int | None = Field(None, alias="privacyCookieExpirationPeriod")
    privacy_cookie_domains: list[str] | None = Field(None, alias="privacyCookieDomains")
    gdpr_data_anonymization: bool | None = Field(None, alias="gdprDataAnonymization")
    sharepoint_integration: bool | None = Field(None, alias="sharepointIntegration")
    gdpr_data_anonymization_mode: GdprDataAnonymizationMode | None = Field(None, alias="gdprDataAnonymizationMode")
    privacy_use_cookies: bool | None = Field(None, alias="privacyUseCookies")
    privacy_use_fingerprinting: bool | None = Field(None, alias="privacyUseFingerprinting")
    cnil: bool | None = Field(None, description="Enable CNIL integration")
    session_id_strict_privacy_mode: bool | None = Field(None, alias="sessionIdStrictPrivacyMode")
    real_time_dashboards: bool | None = Field(None, alias="realTimeDashboards")


class AppAttributes(AppEditableAttributes):
    """Complete app attributes including read-only fields."""

    organization: str | None = Field(None, description="Organization to which app belongs")
    app_type: AppType | None = Field(None, alias="appType")
    added_at: datetime | None = Field(None, alias="addedAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")


class NewAppAttributes(AppEditableAttributes):
    """Attributes for creating a new app."""

    name: str = Field(..., max_length=90, description="App name")
    urls: list[str] = Field(..., description="List of URLs under which the app is available")
    id: str | None = Field(None, description="App UUID")
    app_type: AppType | None = Field(AppType.WEB, alias="appType")


class AppListResponse(BaseModel):
    """Response for app list endpoint."""

    meta: Meta
    data: list[JsonApiResource]


class AppResponse(BaseModel):
    """Response for single app endpoint."""

    data: JsonApiResource
