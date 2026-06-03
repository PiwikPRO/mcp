from uuid import UUID

from piwik_pro_mcp.api.methods.tag_manager.api import TagManagerAPI
from piwik_pro_mcp.api.methods.tag_manager.models import inject_explicit_null_trigger_condition_values
from piwik_pro_mcp.tests.api.utils import _FakeClient


def test_create_trigger_generates_missing_condition_ids():
    fake_client = _FakeClient()
    api = TagManagerAPI(fake_client)

    original_conditions = [
        {
            "variable_id": "var-1",
            "condition_type": "equals",
            "value": "foo",
            "options": {},
        },
        {
            "condition_id": "existing-condition-id",
            "variable_id": "var-2",
            "condition_type": "contains",
            "value": "bar",
            "options": {},
        },
    ]

    api.create_trigger(
        app_id="app-123",
        name="Test trigger",
        trigger_type="event",
        conditions=list(original_conditions),
    )

    sent_conditions = fake_client.last_post["data"]["data"]["attributes"]["conditions"]

    # First condition should get a generated UUID
    generated_id = sent_conditions[0]["condition_id"]
    UUID(generated_id)  # Raises ValueError if not a valid UUID string
    assert "condition_id" not in original_conditions[0]

    # Second condition should preserve the provided UUID
    assert sent_conditions[1]["condition_id"] == "existing-condition-id"
    assert original_conditions[1]["condition_id"] == "existing-condition-id"


def test_create_trigger_preserves_explicit_null_value_for_unary_conditions():
    fake_client = _FakeClient()
    api = TagManagerAPI(fake_client)

    api.create_trigger(
        app_id="app-123",
        name="Unary trigger",
        trigger_type="event",
        conditions=[
            {
                "variable_id": "var-1",
                "condition_type": "is_true",
                "value": None,
                "options": {},
            }
        ],
    )

    sent_conditions = fake_client.last_post["data"]["data"]["attributes"]["conditions"]
    assert sent_conditions[0]["condition_type"] == "is_true"
    assert "value" in sent_conditions[0]
    assert sent_conditions[0]["value"] is None


def test_create_trigger_injects_null_value_when_unary_condition_omits_value_key():
    fake_client = _FakeClient()
    api = TagManagerAPI(fake_client)

    api.create_trigger(
        app_id="app-123",
        name="Unary trigger",
        trigger_type="event",
        conditions=[
            {
                "variable_id": "var-1",
                "condition_type": "is_true",
                "options": {},
            }
        ],
    )

    sent_conditions = fake_client.last_post["data"]["data"]["attributes"]["conditions"]
    assert sent_conditions[0]["value"] is None


def test_create_trigger_allows_relationships_payload():
    fake_client = _FakeClient()
    api = TagManagerAPI(fake_client)

    relationships = {"trigger_group": {"data": {"id": "group-123", "type": "trigger_group"}}}

    api.create_trigger(
        app_id="app-123",
        name="Grouped trigger",
        trigger_type="event",
        relationships=relationships,
    )

    sent_data = fake_client.last_post["data"]["data"]
    assert sent_data["attributes"] == {"name": "Grouped trigger", "trigger_type": "event"}
    assert sent_data["relationships"] == relationships


def test_inject_explicit_null_trigger_condition_values_is_noop_for_comparisons():
    payload: dict = {
        "conditions": [
            {
                "condition_id": "c1",
                "variable_id": "v1",
                "condition_type": "equals",
                "value": "x",
                "options": {},
            }
        ]
    }
    inject_explicit_null_trigger_condition_values(payload)
    assert payload["conditions"][0] == {
        "condition_id": "c1",
        "variable_id": "v1",
        "condition_type": "equals",
        "value": "x",
        "options": {},
    }


def test_update_trigger_allows_relationship_only_payload():
    fake_client = _FakeClient()
    api = TagManagerAPI(fake_client)

    relationships = {"trigger_group": {"data": None}}

    api.update_trigger(
        app_id="app-123",
        trigger_id="trigger-123",
        relationships=relationships,
    )

    sent_data = fake_client.last_patch["data"]["data"]
    assert sent_data == {
        "type": "trigger",
        "id": "trigger-123",
        "relationships": relationships,
    }
