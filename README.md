# 🤖 Piwik PRO MCP Server (beta)

A Model Context Protocol (MCP) server built with the official MCP Python SDK that provides
ability to control Piwik PRO Analytics resources.

## 🎇 Features

- **App Management**: Create, read, update, and delete apps
- **Tracker Settings**: Global and app-specific tracker configuration management
- **Container Settings**:
  - Get installation code for an app
  - Read Container Settings
- **Customer Data Platform**:
  - Create, read, update and delete Audiences
- **Tag Manager Support**: Create, read, update, and delete:
  - Tags
    - Custom Code
    - Custom Event
  - Triggers
    - Click
    - Data Layer Event
    - Page View
  - Variables
    - Constant
    - Custom Javascript
    - Data Layer
    - DOM Element
  - **Version Management**:
    - Publish tag manager versions

## 🚀 Quickstart

Visit your account API Keys section: `https://ACCOUNT.piwik.pro/profile/api-credentials` and generate new credentials.
You will need those three variables for mcp configuration:

- `PIWIK_PRO_HOST` - Your piwik host, `ACCOUNT.piwik.pro`
- `PIWIK_PRO_CLIENT_ID` - Client ID
- `PIWIK_PRO_CLIENT_SECRET` - Client Secret

### MCP Client Configuration

All MCP clients have a dedicated json file in which they store mcp configuration. Depending on client, name and
location of it can differ.

- **Claude Desktop**
  - Go to `Settings -> Developer -> Edit Config` - this will open directory that contains `claude_desktop_config.json`
  - Apply one of the snippets from below
  - Restart application

- **Cursor** - [Official documentation](https://docs.cursor.com/en/context/mcp#configuration-locations)
- **Claude Code** - [Official documentation](https://docs.anthropic.com/en/docs/claude-code/mcp#installing-mcp-servers)

In order to use Piwik PRO mcp server, you need to install
[uv](https://docs.astral.sh/uv/getting-started/installation/) or
[docker](https://docs.docker.com/get-started/get-docker/).

Copy configuration of your preffered option and fill in required env variables.

#### Option #1 - UV

If you don't have `uv`, check the
[official installation guide](https://docs.astral.sh/uv/getting-started/installation/).

```json
{
  "mcpServers": {
    "piwik-pro-analytics": {
      "command": "uvx",
      "args": ["piwik-pro-mcp"],
      "env": {
        "PIWIK_PRO_HOST": "ACCOUNT.piwik.pro",
        "PIWIK_PRO_CLIENT_ID": "CLIENT_ID",
        "PIWIK_PRO_CLIENT_SECRET": "CLIENT_SECRET"
      }
    }
  }
}
```

<details>
<summary><b>🔒 How to keep secrets out of configuration file</b></summary>

It's easier to type environment variables straight into mcp configuration, but keeping them outside of this
file is a more secure way. Create `.piwik-pro-mcp.env` file and put configuration into it:

```env
# .piwik.pro.mcp.env 
PIWIK_PRO_HOST=ACCOUNT.piwik.pro
PIWIK_PRO_CLIENT_ID=CLIENT_ID
PIWIK_PRO_CLIENT_SECRET=CLIENT_SECRET
```

Refer to this file through `--env-file` argument:

```json
{
  "mcpServers": {
    "piwik-pro-analytics": {
      "command": "uvx",
      "args": [
        "piwik-pro-mcp", 
        "--env-file", 
        "/absolute/path/to/.piwik-pro-mcp.env"
      ]
    }
  }
}
```

</details>

#### Option #2 - Docker

You need to have Docker installed – check the [official installation guide](https://www.docker.com/get-started/).

```json
{
  "mcpServers": {
    "piwik-pro-analytics": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "ghcr.io/piwikpro/mcp:latest"
      ],
      "env": {
        "PIWIK_PRO_HOST": "ACCOUNT.piwik.pro",
        "PIWIK_PRO_CLIENT_ID": "CLIENT_ID",
        "PIWIK_PRO_CLIENT_SECRET": "CLIENT_SECRET"
      }
    }
  }
}
```

<details>
<summary><b>🔒 How to keep secrets out of configuration file</b></summary>

It's easier to type environment variables straight into mcp configuration, but keeping them outside of this
file is a more secure way. Create `.piwik-pro-mcp.env` file and put configuration into it:

```env
# .piwik.pro.mcp.env 
PIWIK_PRO_HOST=ACCOUNT.piwik.pro
PIWIK_PRO_CLIENT_ID=CLIENT_ID
PIWIK_PRO_CLIENT_SECRET=CLIENT_SECRET
```

Refer to this file through `--env-file` argument:

```json
{
  "mcpServers": {
    "piwik-pro-analytics": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--env-file",
        "/absolute/path/to/.piwik-pro-mcp.env",
        "ghcr.io/piwikpro/mcp:latest"
      ]
    }
  }
}
```

</details>

Restart your MCP client to apply configuration changes.

## 🪄 First Use

### ⚠️ Proceed with care

Keep in mind that the results produced by AI may sometimes be unexpected or inconsistent. It is important to carefully
review and validate any outputs, as AI-generated solution might not always align perfectly with your requirements or
best practices.

### First prompts

After configuration is done, you can start writing prompts about Piwik PRO resources 🎉. Here are some examples
on which you can test out that integration works correctly.

```
List my Piwik PRO apps.

List tags of <NAME> app.

In app <NAME>, add a new tag, that will show alert("hello") when user enters any page.

Copy tag <NAME> from app <APP> to all apps with <PREFIX> prefix.
```

## 🚦 Roadmap

Current featureset is not complete, and we're planning to add additional functionalities soon:

| Module    | Feature           | ETA     |
| --------- | ----------------- | ------- |
| Analytics | Annotations       | Q4 2025 |
|           | Goals             | Q4 2025 |
|           | Custom Dimensions | Q4 2025 |
|           | Query API         | Q4 2025 |

## 🔈 Feedback

We value your feedback and questions! If you have suggestions, encounter any issues, or want to request new features,
please open an issue on our [GitHub Issues page](https://github.com/piwikpro/mcp/issues). Your input helps us
improve the project and better serve the community.

## 📡 Telemetry

We collect anonymous telemetry data to help us understand how the MCP server is used and to improve its reliability and
features. This telemetry includes information about which MCP tools are invoked and the responses result, either
success or error, but **does not include any personal data, tool arguments, or sensitive information**.

The collected data is used solely for the purpose of identifying issues, prioritizing improvements, and ensuring the
best possible experience for all users.

If you prefer not to send telemetry data, you can opt out at any time by adding the environment variable
`PIWIK_PRO_TELEMETRY=0` to your MCP server configuration.

## 🔧 Available Tools

### Parameter Discovery

- `tools_parameters_get(tool_name)` - Get JSON schema for any tool's parameters

### App Management

- `apps_list(limit, offset, search)` - List all apps with filtering and pagination
- `apps_get(app_id)` - Get detailed information about a specific app
- `apps_create(attributes)` - Create a new app using JSON attributes
- `apps_update(app_id, attributes)` - Update existing app using JSON attributes
- `apps_delete(app_id)` - Delete an app (irreversible)

### Container Settings

- `container_settings_get_installation_code(app_id)` - Get installation code snippet for embedding the container
- `container_settings_list(app_id)` - Get app container settings (JSON:API list with pagination)

### Tag Manager - Tags

- `tags_list(app_id, limit, offset, filters)` - List tags
- `tags_get(app_id, tag_id)` - Get specific tag details
- `tags_create(app_id, attributes)` - Create new tag using JSON attributes
- `tags_update(app_id, tag_id, attributes)` - Update existing tag using JSON attributes
- `tags_delete(app_id, tag_id)` - Delete tag (irreversible)
- `tags_copy(app_id, tag_id, target_app_id?, name?, with_triggers=false)` - Copy a tag within the same app or
  to another app. Supports optional rename and copying attached triggers (set `with_triggers=true`).

### Tag Manager - Relationships

- `tags_list_triggers(app_id, tag_id, limit, offset, sort, name, trigger_type)` - List triggers attached to a tag
- `triggers_list_tags(app_id, trigger_id, limit, offset, sort, name, is_active, template, consent_type, is_prioritized)` - List tags assigned to a trigger

### Tag Manager - Triggers

- `triggers_list(app_id, limit, offset, filters)` - List triggers
- `triggers_get(app_id, trigger_id)` - Get specific trigger details
- `triggers_create(app_id, attributes)` - Create new trigger using JSON attributes
- `triggers_copy(app_id, trigger_id, target_app_id?, name?)` - Copy a trigger within the same app to another
  app. Supports optional rename.

### Tag Manager - Variables

- `variables_list(app_id, limit, offset, filters)` - List variables
- `variables_get(app_id, variable_id)` - Get specific variable details
- `variables_create(app_id, attributes)` - Create new variable using JSON attributes
- `variables_update(app_id, variable_id, attributes)` - Update an existing variable using JSON attributes
- `variables_copy(app_id, variable_id, target_app_id?, name?)` - Copy a variable within the same app or to
  another app. Supports optional rename.

### Tag Manager - supported resources

**Tag Templates:**

- `custom_tag` - Flexible asynchronous tag for custom HTML/JavaScript/CSS code injection

**Trigger Templates:**

- `click` - Click event triggers with element targeting and condition filtering
- `page_view` - Page load triggers with URL pattern matching and user characteristics

**Variable Templates:**

- `constant` - Static value variables for reusable constants across tags
- `custom_javascript` - Dynamic variables using custom JavaScript code execution
- `dom_element` - Extract values from DOM elements using CSS selectors or XPath
- `data_layer` - Read values from data layer objects for enhanced tracking data

### Tag Manager - Template Discovery

- `templates_list()` - List available tag templates
- `templates_get_tag(template_name)` - Get detailed documentation for a tag template
- `templates_list_triggers()` - List available trigger templates
- `templates_get_trigger(template_name)` - Get detailed documentation for a trigger template
- `templates_list_variables()` - List available variable templates
- `templates_get_variable(template_name)` - Get detailed documentation for a variable template

> **Note**: Additional templates for Google Analytics, Piwik PRO, e-commerce tracking, and other platforms are planned for future implementation. The current templates provide a solid foundation for custom tracking implementations.

### Tag Manager - Versions

- `versions_list(app_id, limit, offset)` - List all versions
- `versions_get_draft(app_id)` - Get current draft version
- `versions_get_published(app_id)` - Get published/live version
- `versions_publish_draft(app_id)` - Publish draft to make it live

### Customer Data Platform (CDP)

- `audiences_list(app_id)` - List all audiences for an app
- `audiences_get(app_id, audience_id)` - Get detailed audience information
- `audiences_create(app_id, attributes)` - Create new audience using JSON attributes
- `audiences_update(app_id, audience_id, attributes)` - Update existing audience using JSON attributes
- `audiences_delete(app_id, audience_id)` - Delete an audience (irreversible)
- `activations_attributes_list(app_id)` - List all available CDP attributes for audience creation

### Tracker Settings

- `tracker_settings_global_get()` - Get global tracker settings
- `tracker_settings_global_update(attributes)` - Update global tracker settings using JSON attributes
- `tracker_settings_app_get(app_id)` - Get app-specific tracker settings
- `tracker_settings_app_update(app_id, attributes)` - Update app tracker settings using JSON attributes
- `tracker_settings_app_delete(app_id, setting)` - Delete specific tracker setting

## Development

This project requires [uv](https://github.com/astral-sh/uv) for Python package management. uv is a fast Python package installer and resolver, written in Rust.

## Installation

### Local Installation

1. Install development dependencies:

```bash
uv sync --dev
```

### Running the Server

```bash
# Development server
uv run python -m piwik_pro_mcp.server  # Start MCP server

# Code formatting and linting
uv run ruff check .        # Check for linting issues
uv run ruff format .       # Format code

# Testing
uv run pytest tests/      # Run test suite
uv run pytest tests/ -v   # Run with verbose output
uv run pytest tests/ --cov # Run with coverage report
```

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest 
```

## Architecture

### MCP Module Organization

The project follows a modular architecture that separates concerns and enables easy contribution:

#### Core Components

- **`src/piwik_pro_mcp/server.py`**: Clean FastMCP server creation, configuration, and main entry point with argument parsing
- **`src/piwik_pro_mcp/responses.py`**: MCP-specific Pydantic response models for typed tool outputs
- **`src/piwik_pro_mcp/api/`**: Integrated API client library with OAuth2 authentication
- **`pyproject.toml`**: Modern Python project configuration with uv dependency management

#### Modular Tool Organization

- **`src/piwik_pro_mcp/tools/`**: Organized by functional domains for easy contribution
  - **`apps/tools.py`**: App management operations (create, read, update, delete)
  - **`cdp/`**: Customer Data Platform operations
    - `audiences.py`: Audience management operations
    - `attributes.py`: Attribute discovery operations
    - `tools.py`: CDP tool registration
  - **`container_settings/tools.py`**: Container settings operations
  - **`tag_manager/`**: Tag Manager operations split by resource type
    - `tags.py`: Tag management operations
    - `triggers.py`: Trigger management operations  
    - `variables.py`: Variable management operations
    - `versions.py`: Version management operations
    - `templates.py`: Template discovery and retrieval
  - **`tracker_settings/tools.py`**: Tracker settings operations

#### Shared Utilities

- **`src/piwik_pro_mcp/common/`**: Shared functionality across all tool modules
  - `utils.py`: Client creation and validation utilities
  - `templates.py`: Template loading utilities
  - `tool_schemas.py`: Common tool schema definitions
- **`src/piwik_pro_mcp/tools/parameters.py`**: Parameter discovery and validation
