"""
MCP-specific models for Tag Manager tools.

This module provides Pydantic models used specifically by the MCP Tag Manager tools
for validation and schema generation.
"""

from typing import Any

from pydantic import BaseModel, Field, field_validator

from ...common.settings import tag_manager_resource_check_enabled
from ...common.templates import list_available_assets


class TagCreateAttributes(BaseModel):
    """Base attributes for creating Tag Manager resources."""

    model_config = {"extra": "allow"}  # Allow additional fields for template-specific attributes

    name: str = Field(..., description="Resource name")
    template: str = Field(..., description="Resource template")
    is_active: bool | None = Field(None, description="Whether resource is active")

    # Common template-specific fields that many templates use
    code: str | None = Field(None, description="Tag code (HTML, script, or CSS)")
    consent_type: str | None = Field(None, description="Consent type for privacy compliance")
    tag_type: str | None = Field(None, description="Only using async is not deprecated")
    document_write: bool | None = Field(None, description="Whether tag uses document.write")
    disable_in_debug_mode: bool | None = Field(None, description="Disable in debug mode")
    respect_visitors_privacy: bool | None = Field(None, description="Respect visitor privacy settings")
    priority: int | None = Field(None, description="Tag firing priority")
    template_options: dict[str, Any] | None = Field(None, description="Template-specific options")

    @field_validator("template")
    @classmethod
    def _validate_template(cls, v: str) -> str:
        if not tag_manager_resource_check_enabled():
            return v
        allowed = set(list_available_assets("tag_manager/tags").keys())
        if v not in allowed:
            raise ValueError(f"Unsupported tag template '{v}'. Use templates_list_tags() to discover options.")
        return v


class TagUpdateAttributes(BaseModel):
    """Base attributes for updating Tag Manager resources."""

    model_config = {"extra": "allow"}  # Allow additional fields for template-specific attributes

    name: str | None = Field(None, description="Resource name")
    template: str | None = Field(None, description="Resource template")
    is_active: bool | None = Field(None, description="Whether resource is active")

    # Common template-specific fields that many templates use
    code: str | None = Field(None, description="Tag code (HTML, script, or CSS)")
    consent_type: str | None = Field(None, description="Consent type for privacy compliance")
    tag_type: str | None = Field(None, description="Tag execution type (sync/async)")
    document_write: bool | None = Field(None, description="Whether tag uses document.write")
    disable_in_debug_mode: bool | None = Field(None, description="Disable in debug mode")
    respect_visitors_privacy: bool | None = Field(None, description="Respect visitor privacy settings")
    priority: int | None = Field(None, description="Tag firing priority")
    template_options: dict[str, Any] | None = Field(None, description="Template-specific options")


class TagRelationships(BaseModel):
    """Optional trigger relationships for tags_create and tags_update (MCP tool input)."""

    model_config = {"extra": "forbid"}

    triggers: list[str] | None = Field(
        default=None,
        description=(
            "Trigger UUIDs to attach (discover via triggers_list). "
            'Prefer a flat list of UUID strings, e.g. {"triggers": ["<uuid>"]}. '
            "For compatibility, a bare UUID string or JSON:API-style objects "
            "(with `data[].id`) are accepted and normalized. "
            "Omit or null: on tags_create, create without triggers; on tags_update, keep existing triggers. "
            "Empty list: detach all triggers on tags_update; on tags_create, omit attaching triggers."
        ),
    )

    @field_validator("triggers", mode="before")
    @classmethod
    def _coerce_trigger_ids(cls, value: object) -> list[str] | None:
        if value is None:
            return None
        if isinstance(value, str):
            stripped = value.strip()
            return [stripped] if stripped else []
        if isinstance(value, dict):
            nested = value.get("data", value.get("triggers"))
            if nested is not None:
                return cls._coerce_trigger_ids(nested)
            raise ValueError("triggers must be a list of trigger UUID strings, not a JSON:API object")
        if isinstance(value, list):
            ids: list[str] = []
            for item in value:
                if isinstance(item, str):
                    stripped = item.strip()
                    if not stripped:
                        raise ValueError("each triggers item must be a non-empty trigger UUID string")
                    ids.append(stripped)
                elif isinstance(item, dict):
                    trigger_id = item.get("id")
                    if not isinstance(trigger_id, str) or not trigger_id.strip():
                        raise ValueError(
                            "each triggers item must be a UUID string or an object with a non-empty string id"
                        )
                    ids.append(trigger_id.strip())
                else:
                    raise ValueError("each triggers item must be a UUID string or an object with a non-empty string id")
            return ids
        raise ValueError("triggers must be a list of trigger UUID strings")

    @field_validator("triggers")
    @classmethod
    def _normalize_trigger_ids(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return None
        return [str(item).strip() for item in v if str(item).strip()]


class TriggerRelationshipMemberMeta(BaseModel):
    """Per-link metadata for a related trigger (JSON:API relationship member meta)."""

    model_config = {"extra": "forbid"}

    firing_threshold: int = Field(ge=1, description="Firing threshold for this linked trigger; must be >= 1")


class TriggerRelationshipMember(BaseModel):
    """One related trigger in MCP `relationships.triggers` (plain UUID strings are coerced to id-only)."""

    model_config = {"extra": "forbid"}

    id: str = Field(..., description="UUID of the related trigger resource")
    meta: TriggerRelationshipMemberMeta | None = Field(
        default=None,
        description="Optional meta for this link (e.g. firing_threshold for trigger_group members)",
    )

    @field_validator("id", mode="before")
    @classmethod
    def _strip_id(cls, v: Any) -> str:
        if not isinstance(v, str):
            raise ValueError("id must be a string UUID")
        s = v.strip()
        if not s:
            raise ValueError("id must be non-empty")
        return s


class TriggerRelationships(BaseModel):
    """MCP ``relationships`` for triggers: at most ``triggers`` and ``tags`` (no other keys)."""

    model_config = {"extra": "forbid"}

    triggers: list[TriggerRelationshipMember] | None = Field(
        default=None,
        description=(
            "Related trigger UUIDs for JSON:API `triggers` relationship. Each item may be a UUID string or "
            'an object {"id": "...", "meta": {"firing_threshold": N}} with N >= 1 when meta is present.'
        ),
    )
    tags: list[str] | None = Field(
        default=None,
        description=(
            "Tag UUIDs for JSON:API `tags` relationship (discover via tags_list). "
            "Omit or null: on triggers_create, create without tags; on triggers_update, keep existing tags. "
            "Empty list: clear tag links on triggers_update."
        ),
    )

    @field_validator("triggers", mode="before")
    @classmethod
    def _coerce_triggers_items(cls, v: Any) -> Any:
        if v is None:
            return None
        if not isinstance(v, list):
            raise ValueError("triggers must be a list of UUID strings and/or objects with id and optional meta")
        out: list[Any] = []
        for item in v:
            if isinstance(item, str):
                s = item.strip()
                if s:
                    out.append({"id": s})
            elif isinstance(item, dict):
                out.append(item)
            else:
                raise ValueError("each triggers item must be a UUID string or an object with id and optional meta")
        return out

    @field_validator("tags", mode="before")
    @classmethod
    def _normalize_tag_ids(cls, v: Any) -> list[str] | None:
        if v is None:
            return None
        if not isinstance(v, list):
            raise ValueError("tags must be a list of UUID strings")
        return [str(item).strip() for item in v if str(item).strip()]


class VariableCreateAttributes(BaseModel):
    """Attributes for creating variables with template-specific fields."""

    model_config = {"extra": "allow"}  # Allow additional fields for template-specific attributes

    variable_type: str = Field(..., description="Variable type")
    name: str = Field(..., description="Variable name")
    value: str | None = Field(None, description="Value differs based on variable type")
    options: dict[str, Any] | None = Field(None, description="Template-specific options.")

    @field_validator("variable_type")
    @classmethod
    def _validate_variable_type(cls, v: str) -> str:
        if not tag_manager_resource_check_enabled():
            return v
        allowed = set(list_available_assets("tag_manager/variables").keys())
        if v not in allowed:
            raise ValueError(f"Unsupported variable type '{v}'. Use templates_list_variables() to discover options.")
        return v


class TriggerCreateAttributes(BaseModel):
    """Attributes for creating triggers with assets-based allowlist enforcement."""

    model_config = {"extra": "allow"}

    name: str = Field(..., description="Trigger name")
    trigger_type: str = Field(..., description="Trigger type (must match assets)")

    @field_validator("trigger_type")
    @classmethod
    def _validate_trigger_type(cls, v: str) -> str:
        if not tag_manager_resource_check_enabled():
            return v
        allowed = set(list_available_assets("tag_manager/triggers").keys())
        if v not in allowed:
            raise ValueError(f"Unsupported trigger type '{v}'. Use templates_list_triggers() to discover options.")
        return v


class TriggerUpdateAttributes(BaseModel):
    """Attributes for updating triggers with template-specific fields."""

    model_config = {"extra": "allow"}

    name: str | None = Field(None, description="Trigger name")
    conditions: list[dict[str, Any]] | None = Field(None, description="Trigger conditions")


class VariableUpdateAttributes(BaseModel):
    """Attributes for updating variables with template-specific fields."""

    model_config = {"extra": "allow"}  # Allow additional fields for template-specific attributes

    name: str | None = Field(None, description="Variable name")
    value: str | None = Field(None, description="Value differs based on variable type")
    options: dict[str, Any] | None = Field(None, description="Template-specific options.")


class VersionUpdateAttributes(BaseModel):
    """Attributes for editing a Tag Manager version's name and description.

    Only ``name`` (the commit name) and ``description`` are editable. An omitted
    field is left unchanged; passing an explicit ``null`` clears the field.
    """

    model_config = {"extra": "forbid"}

    name: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="Version name (commit name). Omit to leave unchanged; pass null to clear.",
    )
    description: str | None = Field(
        None,
        min_length=1,
        max_length=65536,
        description="Version description. Omit to leave unchanged; pass null to clear.",
    )


class PublishStatusResponse(BaseModel):
    """Response for version publishing operations."""

    status: str = Field(..., description="Operation status")
    message: str = Field(..., description="Operation details")
    version_info: dict[str, Any] = Field(default_factory=dict, description="Information about the published version")
