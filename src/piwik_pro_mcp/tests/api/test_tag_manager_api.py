from uuid import UUID

from piwik_pro_mcp.api.methods.tag_manager.api import TagManagerAPI
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
