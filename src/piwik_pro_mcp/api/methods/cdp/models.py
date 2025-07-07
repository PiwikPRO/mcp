"""
Pydantic models for Piwik PRO CDP API data structures.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class AudienceAuthor(BaseModel):
    """Audience author information."""

    email: str = Field(..., description="Email of the author")


class ConditionFilter(BaseModel):
    """Filtering criteria for audience conditions."""

    operator: str = Field(..., description="Filtering operator (eq, neq, gt, gte, lt, lte, contains, etc.)")
    value: Union[str, int, float, Dict[str, Any]] = Field(
        ..., description="Filtering value (string, number, or object with unit/value)"
    )
    label: Optional[str] = Field(None, description="Filtering value to display")


class EventTimes(BaseModel):
    """Event occurrence count criteria."""

    operator: str = Field(..., description="Comparison operator for event count")
    value: int = Field(..., description="Number of times event should occur")


class EventDuring(BaseModel):
    """Time limit for behavioral condition to occur."""

    seconds: int = Field(..., description="Time limit in seconds", ge=60, le=2592000, multiple_of=60)
    unit: str = Field(..., description="Display unit for time limit", pattern="^(minutes|hours|days)$")


class EventSubCondition(BaseModel):
    """Individual event sub-condition within event behavioral condition."""

    column_id: str = Field(..., description="Event attribute column ID")
    condition: ConditionFilter = Field(..., description="Filtering criteria for this attribute")
    column_meta: Optional[Dict[str, Any]] = Field(None, description="Column metadata (readonly)")


class EventConditionFilter(BaseModel):
    """Event condition filtering structure (behavioral conditions)."""

    operator: str = Field("and", description="Logical operator (must be 'and')")
    conditions: List[EventSubCondition] = Field(
        ..., description="List of event sub-conditions", min_length=1, max_length=5
    )


class ProfileCondition(BaseModel):
    """Profile-based audience condition."""

    condition_type: str = Field("profile", description="Condition type (must be 'profile')")
    column_id: str = Field(..., description="Profile attribute column ID")
    value_selector: str = Field(..., description="Value selector (first, last, any, none, none_of)")
    condition: ConditionFilter = Field(..., description="Filtering criteria")
    column_meta: Optional[Dict[str, Any]] = Field(None, description="Column metadata (readonly)")


class EventCondition(BaseModel):
    """Event-based audience condition."""

    condition_type: str = Field("event", description="Condition type (must be 'event')")
    times: EventTimes = Field(..., description="Event occurrence criteria")
    during: Optional[EventDuring] = Field(None, description="Optional time window for the behavioral condition")
    condition: EventConditionFilter = Field(..., description="Event behavioral filtering criteria")


class AudienceCondition(BaseModel):
    """Audience condition definition with properly typed conditions."""

    operator: str = Field("or", description="Logical operator (must be 'or')")
    conditions: List[Union[ProfileCondition, EventCondition]] = Field(
        ..., description="List of profile or event conditions"
    )


class AudienceDefinition(BaseModel):
    """Audience definition with conditions."""

    operator: str = Field("and", description="Logical operator (must be 'and')")
    conditions: List[AudienceCondition] = Field(..., description="List of condition groups")


class AudienceListItem(BaseModel):
    """Audience object without definition (for list response)."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., description="ID of the audience")
    app_id: str = Field(..., alias="appId", description="ID of the app")
    created_at: datetime = Field(..., alias="createdAt", description="Audience creation date")
    updated_at: datetime = Field(..., alias="updatedAt", description="Latest audience update date")
    name: str = Field(..., description="Name of the audience")
    description: str = Field(..., description="Description of the audience")
    membership_duration_days: int = Field(
        ..., alias="membershipDurationDays", description="Membership duration in days"
    )
    author: AudienceAuthor = Field(..., description="Author of the audience")
    is_author: bool = Field(..., alias="isAuthor", description="Whether current user is the author")
    version: int = Field(..., description="Version of the audience")


class AudienceDetail(AudienceListItem):
    """Full audience object with definition."""

    definition: AudienceDefinition = Field(..., description="Audience definition")


class NewAudienceAttributes(BaseModel):
    """Attributes for creating a new audience."""

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., max_length=100, description="Audience name")
    description: str = Field(..., max_length=200, description="Audience description")
    definition: AudienceDefinition = Field(..., description="Audience definition")
    membership_duration_days: int = Field(
        ..., alias="membership_duration_days", description="Membership duration in days"
    )


class EditableAudienceAttributes(BaseModel):
    """Attributes for updating an existing audience."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    name: str = Field(..., max_length=100, description="Audience name")
    description: str = Field(..., max_length=200, description="Audience description")
    definition: AudienceDefinition = Field(..., description="Audience definition")
    membership_duration_days: int = Field(
        ..., alias="membership_duration_days", description="Membership duration in days"
    )


class AudienceListResponse(BaseModel):
    """Response for audience list endpoint."""

    audiences: List[AudienceListItem] = Field(..., description="List of audiences")


class AudienceResponse(BaseModel):
    """Response for single audience endpoint."""

    audience: AudienceDetail = Field(..., description="Audience details")
