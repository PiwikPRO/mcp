# 🤖 Piwik PRO MCP Server (beta)

A Model Context Protocol (MCP) server built with the official MCP Python SDK that lets you control Piwik PRO Analytics resources.

## 🎇 Features

### 💬 Query API — Have a conversation with your analytics data

Turn questions into insights. The Query API lets you explore your analytics data using natural language. Ask about visitors, page views, conversions, and more without navigating complex dashboards or building reports manually.

- Run flexible queries with custom date ranges and filters
- Discover available dimensions and metrics
- Get answers to analytics questions in seconds

### 📊 Manage Analytics

Keep your analytics setup organized without leaving your the conversation with your AI assistant:

- **Annotations** — Add notes to mark important events, campaigns, or changes
- **Goals** — Set up and manage conversion tracking
- **Custom dimensions** — Extend your tracking with custom data points

### 🏷️ Control Tag Manager

Manage your tracking setup without touching your website code:

- **Tags** — Create and configure tracking tags
- **Triggers** — Define when and where tags fire
- **Variables** — Store and reuse dynamic values
- **Version control** — Publish changes when you're ready

### 🎯 Build audiences with Data Activation (DA)

Build and manage your audience segments:

- Create targeted audiences based on user behavior
- Update segmentation rules in real time

### ⚙️ Configuration and settings

Fine-tune your Piwik PRO setup:

- **App management** — Organize your sites and apps
- **Tracker settings** — Configure tracking behavior globally or for each app
- **Container settings** — Access installation code and container configuration

## 🚀 Quickstart

Go to your account's API credentials page: `https://ACCOUNT.piwik.pro/profile/api-credentials`, then generate new credentials.

You will need these three variables for the MCP configuration:

- `PIWIK_PRO_HOST` - Your piwik host, `ACCOUNT.piwik.pro`
- `PIWIK_PRO_CLIENT_ID` - Client ID
- `PIWIK_PRO_CLIENT_SECRET` - Client Secret

### MCP Client configuration

All of these MCP clients use a JSON file to store the MCP configuration. The file name and location vary by client.

- **Claude Desktop**
  - Go to `Settings -> Developer -> Edit Config`to open the folder containing `claude_desktop_config.json`.
  - Apply one of the snippets from below.
  - Restart the application.

- **Cursor** - The [official documentation](https://docs.cursor.com/en/context/mcp#configuration-locations)
- **Claude Code** - The [official documentation](https://docs.anthropic.com/en/docs/claude-code/mcp#installing-mcp-servers)

To use Piwik PRO MCP server, you need to install
[uv](https://docs.astral.sh/uv/getting-started/installation/) or
[docker](https://docs.docker.com/get-started/get-docker/).

Copy the configuration of your preferred option and enter the required environment variables.

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
<summary><b>🔒 How to keep secrets out of the configuration file</b></summary>

You can enter environment variables directly in the MCP configuration, but storing them in a separate
file is more secure. Create a `.piwik-pro-mcp.env` file and add configuration to it:

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

You need to have Docker installed. See the [official installation guide](https://www.docker.com/get-started/).

```json
{
  "mcpServers": {
    "piwik-pro-analytics": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "ghcr.io/piwikpro/mcp:latest"],
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

You can enter environment variables directly in the MCP configuration, but storing them in a separate
file is more secure. Create a `.piwik-pro-mcp.env` file and add the configuration to it:

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

You're all set! The server starts in **safe mode** by default, so you can explore your analytics data without worrying about accidental changes.

Try these prompts to get started:

```
List my Piwik PRO apps.

List tags in <NAME> app.

What were the top 10 pages last week?

Show me conversion trends from the last month.
```

### Ready to make changes?

Once you're comfortable, disable safe mode to enable t create, update, and delete operations:

```
PIWIK_PRO_SAFE_MODE=0
```

Then try prompts like:

```
In app <NAME>, add a new tag that shows alert("hello") on every page.

Copy the tag <NAME> from app <APP> to all apps with the <PREFIX> prefix.
```

### Other options

- `PIWIK_PRO_TELEMETRY` (default `1`): Controls anonymous usage telemetry. Set this to `0` to disable it.
- `PIWIK_PRO_TM_RESOURCE_CHECK` (default `1`): Enables Tag Manager template validation. Set to `0` to bypass when experimenting with custom templates.

## 🔈 Feedback

We value your feedback and questions. If you have suggestions, run into issues, or want to request a feature,
open an issue on our [GitHub Issues page](https://github.com/piwikpro/mcp/issues). Your feedback helps us
improve the project and support the community.

## 📡 Telemetry

We collect anonymous telemetry data to help us understand how the MCP server is used and to improve its reliability and
features. This telemetry includes information about which MCP tools are invoked and whether the result is a
success or an error, but it **doesn't include any personal data, tool arguments, or sensitive information**.

We use this data only to identify issues, prioritize improvements, and provide the best possible experience for all users.

If you prefer not to send telemetry data, you can opt out at any time by adding the following environment variable
`PIWIK_PRO_TELEMETRY=0` to your MCP server configuration.

## 📚 Documentation

| Document                                 | Description                               |
| ---------------------------------------- | ----------------------------------------- |
| [Available Tools](docs/TOOLS.md)         | Complete reference for all MCP tools      |
| [Development Guide](docs/DEVELOPMENT.md) | Setup, running, testing, and architecture |
| [Contributing](CONTRIBUTION.md)          | How to contribute to the project          |
