## Setup & Verify

- Use `uv` for everything. Install deps with `uv sync --dev`.
- Python requirement is `>=3.12`.
- Run the server with `uv run python -m piwik_pro_mcp.server` or `uv run piwik-pro-mcp`.
- Match CI before finishing: `uv run pytest -v --tb=short`, `uv run ruff check . --config pyproject.toml`, then `uv run ruff format --check . --config pyproject.toml`.
- For focused checks, tests live under `src/piwik_pro_mcp/tests`, so use commands like `uv run pytest src/piwik_pro_mcp/tests/test_server.py::TestMain::test_main_defaults_to_stdio_transport -v`.

## Architecture

- This is a single Python package rooted at `src/piwik_pro_mcp`.
- Main entrypoint and CLI wiring live in `src/piwik_pro_mcp/server.py`.
- Public package layout is split mainly across `api/`, `common/`, `tools/`, `assets/`, and `tests/` under `src/piwik_pro_mcp/`.
- MCP tool registration is centralized in `src/piwik_pro_mcp/tools/__init__.py`; add new registrations there via the domain `register_*` function.
- Environment-driven behavior is centralized in `src/piwik_pro_mcp/common/settings.py`.
- Runtime schema discovery for JSON-style tool attributes is `tools_parameters_get` in `src/piwik_pro_mcp/tools/parameters.py`.

## Configuration

- Required env vars: `PIWIK_PRO_HOST`, `PIWIK_PRO_CLIENT_ID`, `PIWIK_PRO_CLIENT_SECRET`.
- Optional env vars commonly affecting behavior: `PIWIK_PRO_SAFE_MODE`, `PIWIK_PRO_TELEMETRY`, `PIWIK_PRO_TM_RESOURCE_CHECK`, `PIWIK_PRO_HTTP_ALLOWED_HOSTS`.
- `.env` files are supported via `python-dotenv`.

## Behavioral Gotchas

- Safe mode is on by default. `filter_write_tools()` removes any tool without `annotations.readOnlyHint=True`, so read-only tools must be annotated correctly or they disappear from the exposed server.
- `src/piwik_pro_mcp/tests/test_integration.py` is the enforced inventory of registered tools. When adding or removing tools, update the `READ_ONLY_TOOLS` or `WRITE_TOOLS` lists there.
- Settings helpers in `common/settings.py` use `@cache`. Tests that patch `PIWIK_PRO_SAFE_MODE`, `PIWIK_PRO_TELEMETRY`, `PIWIK_PRO_TM_RESOURCE_CHECK`, or `PIWIK_PRO_HTTP_ALLOWED_HOSTS` must clear caches before and after, following `src/piwik_pro_mcp/tests/conftest.py`, `src/piwik_pro_mcp/tests/common/test_settings.py`, and `src/piwik_pro_mcp/tests/test_telemetry.py`.
- If a tool accepts free-form `attributes`, keep its `tools_parameters_get` schema path working and add or maintain the corresponding MCP tests under `src/piwik_pro_mcp/tests/tools/`.

## Transport Notes

- Default transport is `stdio`.
- HTTP mode is `streamable-http` with `http` accepted as an alias.
- Standard HTTP invocation is `uv run piwik-pro-mcp --transport streamable-http --host 0.0.0.0 --port 8000 --path /mcp`.
- The unauthenticated `/health` endpoint exists only in HTTP transport.
- HTTP host allow-list behavior comes from `PIWIK_PRO_HTTP_ALLOWED_HOSTS`; localhost variants are always allowed by default.

## Sources Of Truth

- Prefer `pyproject.toml`, `.github/workflows/ci.yaml`, and the files under `src/piwik_pro_mcp/` over prose.
- Prefer project configuration and source files over editor-specific rules when they conflict.
