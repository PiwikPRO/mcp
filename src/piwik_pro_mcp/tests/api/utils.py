class _FakeClient:
    """Fake HTTP client for API layer tests."""

    def __init__(self, response=None):
        self.response = response
        self.last_request = None
        self.last_get = None
        self.last_post = None

    def get(self, url, params=None, extra_headers=None):
        request_data = {"url": url, "params": params, "headers": extra_headers}
        self.last_request = request_data
        self.last_get = request_data
        return self.response

    def post(self, url, data=None):
        request_data = {"url": url, "data": data}
        self.last_request = request_data
        self.last_post = request_data
        return self.response
