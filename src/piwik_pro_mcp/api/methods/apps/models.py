"""
Pydantic models for Piwik PRO Apps API data structures.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

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

    name: Optional[str] = Field(None, max_length=90, description="App name")
    urls: Optional[List[str]] = Field(None, description="List of URLs under which the app is available")
    timezone: Optional[str] = Field(None, description="App timezone (IANA format)")
    currency: Optional[str] = Field(None, description="App currency")
    e_commerce_tracking: Optional[bool] = Field(None, alias="eCommerceTracking")
    delay: Optional[int] = Field(None, description="Delay in ms")
    gdpr: Optional[bool] = Field(None, description="Enable GDPR compliance")
    gdpr_user_mode_enabled: Optional[bool] = Field(None, alias="gdprUserModeEnabled")
    privacy_cookie_domains_enabled: Optional[bool] = Field(None, alias="privacyCookieDomainsEnabled")
    privacy_cookie_expiration_period: Optional[int] = Field(None, alias="privacyCookieExpirationPeriod")
    privacy_cookie_domains: Optional[List[str]] = Field(None, alias="privacyCookieDomains")
    gdpr_data_anonymization: Optional[bool] = Field(None, alias="gdprDataAnonymization")
    sharepoint_integration: Optional[bool] = Field(None, alias="sharepointIntegration")
    gdpr_data_anonymization_mode: Optional[GdprDataAnonymizationMode] = Field(None, alias="gdprDataAnonymizationMode")
    privacy_use_cookies: Optional[bool] = Field(None, alias="privacyUseCookies")
    privacy_use_fingerprinting: Optional[bool] = Field(None, alias="privacyUseFingerprinting")
    cnil: Optional[bool] = Field(None, description="Enable CNIL integration")
    session_id_strict_privacy_mode: Optional[bool] = Field(None, alias="sessionIdStrictPrivacyMode")
    real_time_dashboards: Optional[bool] = Field(None, alias="realTimeDashboards")


class AppAttributes(AppEditableAttributes):
    """Complete app attributes including read-only fields."""

    organization: Optional[str] = Field(None, description="Organization to which app belongs")
    app_type: Optional[AppType] = Field(None, alias="appType")
    added_at: Optional[datetime] = Field(None, alias="addedAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")


class NewAppAttributes(AppEditableAttributes):
    """Attributes for creating a new app."""

    name: str = Field(..., max_length=90, description="App name")
    urls: List[str] = Field(..., description="List of URLs under which the app is available")
    id: Optional[str] = Field(None, description="App UUID")
    app_type: Optional[AppType] = Field(AppType.WEB, alias="appType")


class AppListResponse(BaseModel):
    """Response for app list endpoint."""

    meta: Meta
    data: List[JsonApiResource]


class AppResponse(BaseModel):
    """Response for single app endpoint."""

    data: JsonApiResource
