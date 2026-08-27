# Development Guide

This guide covers setting up the development environment, running the server, testing, and the project architecture.

## Prerequisites

This project requires [uv](https://github.com/astral-sh/uv) for Python package management. uv is a fast Python package installer and resolver, written in Rust.

Install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Installation

Install development dependencies:

```bash
uv sync --dev
```

## Running the Server

```bash
# Start MCP server (development)
uv run python -m piwik_pro_mcp.server

# Or using the package entry point
uv run piwik-pro-mcp
```

## Code Quality

```bash
# Check for linting issues
uv run ruff check .

# Format code
uv run ruff format .
```

## Testing

```bash
# Run all tests
uv run pytest

# Run test suite
uv run pytest src/piwik_pro_mcp/tests/

# Run with verbose output
uv run pytest src/piwik_pro_mcp/tests/ -v

# Run with coverage report
uv run pytest src/piwik_pro_mcp/tests/ --cov

# Run integration tests only
uv run pytest src/piwik_pro_mcp/tests/test_integration.py -v
```

> **Important:** Always use `uv run pytest`, never `pytest` directly.

## Environment Variables

Required for running with a real Piwik PRO instance:

```bash
export PIWIK_PRO_HOST="your-instance.piwik.pro"
export PIWIK_PRO_CLIENT_ID="your-client-id"
export PIWIK_PRO_CLIENT_SECRET="your-client-secret"
```

You can also use a `.env` file (supported via python-dotenv).

## HTTP Transport

By default the server communicates over `stdio`. The optional `streamable-http` transport opens an HTTP endpoint for MCP clients that connect over the network instead of stdio.

> **Security warning — local use only**
>
> The HTTP transport does **not** authenticate incoming MCP requests. Anyone who can reach the server can invoke all exposed MCP tools, using the server's configured Piwik PRO API credentials (within that token's permissions).
>
> This transport is intended for **local development only**. The default bind address is `127.0.0.1`. **Do not expose the server to the public internet** or untrusted networks without placing it behind your own authentication layer (for example, a reverse proxy with access controls).
>
> For typical MCP client use, prefer the default `stdio` transport, which does not open a network port. Authentication for remote MCP deployments is planned as part of the Remote MCP initiative.

To run the server with HTTP transport locally:

```bash
uv run piwik-pro-mcp --transport streamable-http --host 127.0.0.1 --port 8000 --path /mcp
```

Options:

- `--host` defaults to `127.0.0.1`; keep this for local use. Only bind to `0.0.0.0` on a trusted network if you understand the security implications above
- `--port` defaults to `8000`; adjust to fit your environment or reverse proxy
- `--path` defaults to `/mcp`, matching the SDK client expectations
- `--transport http` may be used as an alias for `streamable-http`

MCP configuration for HTTP transport:

```json
{
  "mcpServers": {
    "piwik-pro-analytics": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

## Docker

Build the Docker image:

```bash
docker build -t mcp-piwik-pro .
```

## Architecture

### Project Structure

```
src/piwik_pro_mcp/
├── server.py           # FastMCP server creation, configuration, main entry point
├── responses.py        # MCP-specific Pydantic response models
├── api/                # API client library
│   ├── client.py       # Main HTTP client with OAuth2 authentication
│   ├── auth.py         # Client credentials flow implementation
│   ├── config.py       # Configuration management
│   ├── exceptions.py   # Custom exception hierarchy
│   └── methods/        # API endpoint implementations
│       ├── apps/       # Apps management API
│       ├── analytics/  # Analytics API
│       ├── cdp/        # Customer Data Platform API
│       ├── container_settings/
│       ├── tag_manager/
│       └── tracker_settings/
├── tools/              # MCP tool implementations
│   ├── analytics/      # Analytics tools (annotations, goals, custom dimensions, query)
│   ├── apps/           # App management tools
│   ├── cdp/            # CDP tools (audiences, attributes)
│   ├── container_settings/
│   ├── tag_manager/    # Tags, triggers, variables, versions, templates
│   ├── tracker_settings/
│   └── parameters.py   # Parameter discovery tool
├── common/             # Shared utilities
│   ├── utils.py        # Client creation, validation utilities
│   ├── templates.py    # Template loading utilities
│   ├── tool_schemas.py # Tool parameter schema mappings
│   └── settings.py     # Configuration management
├── assets/             # Template assets and examples
└── tests/              # Test suite
    ├── test_integration.py
    ├── api/            # API client tests
    └── tools/          # Tool-specific tests
```

### Core Components

- **`server.py`**: Clean FastMCP server creation, configuration, and main entry point with argument parsing
- **`responses.py`**: MCP-specific Pydantic response models for typed tool outputs
- **`api/`**: Integrated API client library with OAuth2 authentication
- **`api/methods/`**: API endpoint modules organized by domain

### Modular Tool Organization

Tools are organized by functional domain in `src/piwik_pro_mcp/tools/`:

- **`analytics/`**: Analytics operations
  - `annotations.py`: User/System annotations tools
  - `goals.py`: Goals management tools
  - `custom_dimensions.py`: Custom dimensions tools
  - `query.py`: Query API tools
- **`apps/tools.py`**: App management operations
- **`cdp/`**: Customer Data Platform operations
  - `audiences.py`: Audience management
  - `attributes.py`: Attribute discovery
- **`container_settings/tools.py`**: Container settings operations
- **`tag_manager/`**: Tag Manager operations
  - `tags.py`, `triggers.py`, `variables.py`, `versions.py`, `templates.py`
- **`tracker_settings/tools.py`**: Tracker settings operations

### Shared Utilities

- **`common/utils.py`**: Client creation (`create_piwik_client`) and validation utilities (`validate_data_against_model`)
- **`common/templates.py`**: Template loading utilities
- **`common/tool_schemas.py`**: Tool parameter schema mappings for `tools_parameters_get`
- **`common/settings.py`**: Configuration management with environment variable parsing

### Key Design Patterns

1. **Unified Architecture**: API client logic is integrated within the MCP module
2. **Error Handling**: MCP tools wrap all exceptions in `RuntimeError` with descriptive messages
3. **Type Safety**: Full type annotations with Pydantic validation
4. **Authentication**: OAuth2 client credentials with automatic token refresh
5. **Safe Mode**: Tools marked with `readOnlyHint: True` are available in safe mode
