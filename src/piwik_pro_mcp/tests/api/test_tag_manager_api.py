import time
from uuid import UUID

import pytest

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


def test_update_version_sends_name_and_description():
    fake_client = _FakeClient()
    api = TagManagerAPI(fake_client)

    api.update_version(
        app_id="app-123",
        version_id="version-123",
        attributes={"name": "Release 1.0", "description": "Adds a few tags and triggers"},
    )

    assert fake_client.last_patch["url"] == "/api/tag/v1/app-123/versions/version-123"
    sent_data = fake_client.last_patch["data"]["data"]
    assert sent_data == {
        "type": "version",
        "id": "version-123",
        "attributes": {"name": "Release 1.0", "description": "Adds a few tags and triggers"},
    }


def test_update_version_sends_only_provided_attributes():
    fake_client = _FakeClient()
    api = TagManagerAPI(fake_client)

    api.update_version(app_id="app-123", version_id="version-123", attributes={"name": "Only name"})

    sent_data = fake_client.last_patch["data"]["data"]
    assert sent_data["attributes"] == {"name": "Only name"}


def test_update_version_sends_explicit_null_to_clear_attributes():
    fake_client = _FakeClient()
    api = TagManagerAPI(fake_client)

    api.update_version(app_id="app-123", version_id="version-123", attributes={"name": None, "description": None})

    sent_data = fake_client.last_patch["data"]["data"]
    assert sent_data["attributes"] == {"name": None, "description": None}


class _PollingFakeClient:
    def __init__(self, responses: list[dict]):
        self.responses = list(responses)
        self.get_calls: list[str] = []

    def get(self, url, params=None, extra_headers=None):
        self.get_calls.append(url)
        if not self.responses:
            raise AssertionError("No more mocked responses")
        return self.responses.pop(0)


def test_wait_for_operation_returns_when_completed():
    fake_client = _PollingFakeClient(
        [
            {"data": {"id": "op-1", "attributes": {"state": "started"}}},
            {"data": {"id": "op-1", "attributes": {"state": "completed", "operation_type": "create_snapshot"}}},
        ]
    )
    api = TagManagerAPI(fake_client)

    result = api.wait_for_operation("app-123", "op-1", poll_interval_seconds=0, timeout_seconds=5)

    assert result["data"]["attributes"]["state"] == "completed"
    assert len(fake_client.get_calls) == 2
    assert fake_client.get_calls[0] == "/api/tag/v1/app-123/operations/op-1"


def test_wait_for_operation_raises_when_failed():
    fake_client = _PollingFakeClient(
        [{"data": {"id": "op-1", "attributes": {"state": "failed", "operation_type": "publish"}}}]
    )
    api = TagManagerAPI(fake_client)

    try:
        api.wait_for_operation("app-123", "op-1", poll_interval_seconds=0, timeout_seconds=5)
        raise AssertionError("Expected RuntimeError")
    except RuntimeError as exc:
        assert "Operation op-1 failed (type: publish)" in str(exc)


def test_wait_for_operation_raises_on_timeout():
    fake_client = _PollingFakeClient([{"data": {"id": "op-1", "attributes": {"state": "started"}}}] * 3)
    api = TagManagerAPI(fake_client)

    try:
        api.wait_for_operation("app-123", "op-1", poll_interval_seconds=0, timeout_seconds=0)
        raise AssertionError("Expected RuntimeError")
    except RuntimeError as exc:
        assert "Timed out after 0s waiting for operation op-1" in str(exc)


def test_wait_for_operation_caps_sleep_to_remaining_timeout(monkeypatch):
    fake_client = _PollingFakeClient([{"data": {"id": "op-1", "attributes": {"state": "started"}}}] * 5)
    api = TagManagerAPI(fake_client)

    current_time = 0.0
    sleep_calls: list[float] = []

    def fake_monotonic() -> float:
        return current_time

    def fake_sleep(seconds: float) -> None:
        nonlocal current_time
        sleep_calls.append(seconds)
        current_time += seconds

    monkeypatch.setattr(time, "monotonic", fake_monotonic)
    monkeypatch.setattr(time, "sleep", fake_sleep)

    with pytest.raises(RuntimeError, match="Timed out after 2s waiting for operation op-1"):
        api.wait_for_operation("app-123", "op-1", poll_interval_seconds=5.0, timeout_seconds=2.0)

    assert sleep_calls == [2.0]
