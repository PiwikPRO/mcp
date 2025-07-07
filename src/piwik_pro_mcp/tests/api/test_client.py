from piwik_pro_mcp.api.client import PiwikProClient


def test_request_forwards_query_params(monkeypatch):
    client = PiwikProClient(host="https://example.com", client_id="id", client_secret="secret")

    # Avoid real auth header resolution
    monkeypatch.setattr(client, "_get_headers", lambda extra_headers=None: {})

    captured = {}

    def fake_request(*, method, url, headers=None, params=None, json=None, timeout=None):
        captured["method"] = method
        captured["url"] = url
        captured["headers"] = headers
        captured["params"] = params
        captured["json"] = json
        captured["timeout"] = timeout

        class _Resp:
            status_code = 200

            def json(self):
                return {}

        return _Resp()

    # Replace the session.request with our fake implementation
    monkeypatch.setattr(client.session, "request", fake_request, raising=False)

    params = {"limit": 10, "offset": 20, "sort": "-createdAt"}
    client.request("GET", "/api/test", params=params)

    assert captured["params"] == params
    assert captured["method"] == "GET"
    assert captured["url"].endswith("/api/test")


def test_method_wrappers_forward_params(monkeypatch):
    client = PiwikProClient(host="https://example.com", client_id="id", client_secret="secret")

    # Avoid real auth header resolution
    monkeypatch.setattr(client, "_get_headers", lambda extra_headers=None: {})

    calls = []

    def fake_request(*, method, url, headers=None, params=None, json=None, timeout=None):
        calls.append(
            {
                "method": method,
                "url": url,
                "params": params,
                "json": json,
            }
        )

        class _Resp:
            status_code = 200

            def json(self):
                return {}

        return _Resp()

    monkeypatch.setattr(client.session, "request", fake_request, raising=False)

    params = {"limit": 5}
    client.get("/api/test", params=params)
    client.post("/api/test", params=params)
    client.patch("/api/test", params=params)
    client.delete("/api/test", params=params)

    assert [c["method"] for c in calls] == ["GET", "POST", "PATCH", "DELETE"]
    for c in calls:
        assert c["url"].endswith("/api/test")
        assert c["params"] == params
