"""API-layer tests for Container Settings write endpoints."""

from piwik_pro_mcp.api.methods.container_settings.api import ContainerSettingsAPI
from piwik_pro_mcp.tests.api.utils import _FakeClient


def test_update_app_settings_sends_patch_with_data_list():
    fake_client = _FakeClient()
    api = ContainerSettingsAPI(fake_client)

    settings = [
        {
            "id": "automatic_scroll_tracking",
            "type": "container/app/setting",
            "attributes": {"value": {"is_enabled": True, "thresholds": [25, 50, 75]}},
        },
        {
            "id": "tracking_domain",
            "type": "container/app/setting",
            "attributes": {"value": "analytics.example.com"},
        },
    ]

    api.update_app_settings(app_id="app-123", settings=settings)

    assert fake_client.last_patch["url"] == "/api/container-settings/v1/app/app-123/settings"
    assert fake_client.last_patch["data"] == {"data": settings}


def test_delete_app_setting_sends_delete_to_setting_url():
    fake_client = _FakeClient()
    api = ContainerSettingsAPI(fake_client)

    api.delete_app_setting(app_id="app-123", setting_name="automatic_scroll_tracking")

    assert fake_client.last_delete["url"] == (
        "/api/container-settings/v1/app/app-123/settings/automatic_scroll_tracking"
    )
