"""
MCP input models for editing Piwik PRO container settings.

Each container setting is modelled as its own class inheriting from the abstract
:class:`ContainerSetting`. A setting encapsulates everything that is specific to it
(its ``id``, its ``value`` shape) while the base owns the shared JSON:API
serialization. Adding a new setting means adding one small class and listing it in
``CONTAINER_APP_SETTINGS`` / ``ContainerAppSetting`` — no existing model grows.
"""

from abc import ABC
from typing import Annotated, Any, ClassVar, Literal

from pydantic import BaseModel, Field, field_validator

# String-valued settings (hostnames and paths) are constrained only to ``min_length=1`` here.
# The backend is the authoritative validator for their formats (``format: hostname`` / ``format:
# path``); it accepts values a client-side pattern would wrongly reject — e.g. templated paths like
# "/tracking/{{ app_id }}.js" — so we deliberately do not re-implement format checks in the tool.

# --- Value models (the ``value`` payload of a setting) -----------------------------


class IsEnabledValue(BaseModel):
    """Value shape for simple on/off settings (spa_tracking, fpc)."""

    model_config = {"extra": "forbid"}

    is_enabled: bool = Field(..., description="Whether the setting is enabled")


class AutomaticScrollTrackingValue(BaseModel):
    """Value shape for the automatic scroll tracking setting."""

    model_config = {"extra": "forbid"}

    is_enabled: bool = Field(..., description="Whether automatic scroll tracking is enabled")
    thresholds: list[Annotated[int, Field(ge=0, le=100)]] = Field(
        ...,
        min_length=1,
        description=(
            "Scroll tracking thresholds: non-empty collection of unique integers from 0 to 100. "
            "Always required (even when disabling); a common default is [5, 50, 95]."
        ),
    )

    @field_validator("thresholds")
    @classmethod
    def _thresholds_must_be_unique(cls, value: list[int]) -> list[int]:
        if len(value) != len(set(value)):
            raise ValueError("thresholds must be unique")
        return value


# --- Abstract base + per-setting classes -------------------------------------------


class ContainerSetting(BaseModel, ABC):
    """Abstract base for a single app container setting.

    Concrete subclasses declare ``id`` (a ``Literal`` used as the discriminator) and a
    concrete ``value`` type. The base owns the JSON:API envelope so subclasses never
    reimplement serialization. This class is not instantiated directly.
    """

    model_config = {"extra": "forbid"}

    RESOURCE_TYPE: ClassVar[str] = "container/app/setting"

    id: str = Field(..., description="Container setting name")
    value: Any = Field(..., description="Container setting value")

    def to_jsonapi_item(self) -> dict[str, Any]:
        """Serialize this setting into a JSON:API resource object for the API payload."""
        value = self.value.model_dump(mode="json") if isinstance(self.value, BaseModel) else self.value
        return {"id": self.id, "type": self.RESOURCE_TYPE, "attributes": {"value": value}}


class AutomaticScrollTrackingSetting(ContainerSetting):
    id: Literal["automatic_scroll_tracking"] = "automatic_scroll_tracking"
    value: AutomaticScrollTrackingValue


class SpaTrackingSetting(ContainerSetting):
    id: Literal["spa_tracking"] = "spa_tracking"
    value: IsEnabledValue


class FpcSetting(ContainerSetting):
    id: Literal["fpc"] = "fpc"
    value: IsEnabledValue


class TrackingDomainSetting(ContainerSetting):
    id: Literal["tracking_domain"] = "tracking_domain"
    value: str = Field(..., min_length=1, description="Tracking domain (hostname)")


class StaticResourcesDomainSetting(ContainerSetting):
    id: Literal["static_resources_domain"] = "static_resources_domain"
    value: str = Field(..., min_length=1, description="Static resources domain (hostname)")


class UiApisDomainSetting(ContainerSetting):
    id: Literal["ui_apis_domain"] = "ui_apis_domain"
    value: str = Field(..., min_length=1, description="UI & APIs domain (hostname)")


class ContainerJsPathSetting(ContainerSetting):
    id: Literal["container_js_path"] = "container_js_path"
    value: str = Field(..., min_length=1, description="ContainerJS path")


class TrackingScriptPathSetting(ContainerSetting):
    id: Literal["tracking_script_path"] = "tracking_script_path"
    value: str = Field(..., min_length=1, description="Tracking script path")


class TrackingEndpointPathSetting(ContainerSetting):
    id: Literal["tracking_endpoint_path"] = "tracking_endpoint_path"
    value: str = Field(..., min_length=1, description="Tracking endpoint path")


# --- Registration point (the single place to list a new setting) -------------------

CONTAINER_APP_SETTINGS: tuple[type[ContainerSetting], ...] = (
    AutomaticScrollTrackingSetting,
    SpaTrackingSetting,
    FpcSetting,
    TrackingDomainSetting,
    StaticResourcesDomainSetting,
    UiApisDomainSetting,
    ContainerJsPathSetting,
    TrackingScriptPathSetting,
    TrackingEndpointPathSetting,
)

#: Valid setting names, derived from the registered classes (used e.g. to validate deletes).
CONTAINER_APP_SETTING_NAMES: tuple[str, ...] = tuple(cls.model_fields["id"].default for cls in CONTAINER_APP_SETTINGS)

#: Discriminated union over all settings — Pydantic routes each item by its ``id``.
ContainerAppSetting = Annotated[
    AutomaticScrollTrackingSetting
    | SpaTrackingSetting
    | FpcSetting
    | TrackingDomainSetting
    | StaticResourcesDomainSetting
    | UiApisDomainSetting
    | ContainerJsPathSetting
    | TrackingScriptPathSetting
    | TrackingEndpointPathSetting,
    Field(discriminator="id"),
]


class ContainerAppSettingsUpdate(BaseModel):
    """Attributes for updating one or more of an app's container settings.

    Each item in ``data`` is one setting, identified by ``id`` and carrying its
    setting-specific ``value``.
    """

    model_config = {"extra": "forbid"}

    data: list[ContainerAppSetting] = Field(
        ...,
        min_length=1,
        description="List of container settings to update; each item is {id, value} for one setting",
    )
