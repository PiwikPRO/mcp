# 🤖 Piwik PRO MCP Server (beta)

A Model Context Protocol (MCP) server built with the official MCP Python SDK that provides
ability to control Piwik PRO Analytics resources.

## 🎇 Features

### 💬 Query API — Have a Conversation with Your Analytics Data

Turn questions into insights. The Query API lets you explore your analytics data naturally — ask about visitors, page views, conversions, and more. No need to navigate complex dashboards or build reports manually.

- Execute flexible queries with custom date ranges and filters
- Discover all available dimensions and metrics
- Get answers in seconds, not clicks

### 📊 Analytics Management

Keep your analytics organized without leaving your workflow:

- **Annotations** — Add notes to mark important events, campaigns, or changes
- **Goals** — Set up and manage conversion tracking
- **Custom Dimensions** — Extend your tracking with custom data points

### 🏷️ Tag Manager

Deploy and manage tracking without touching your website code:

- **Tags** — Create and configure tracking tags
- **Triggers** — Define when and where tags fire
- **Variables** — Store and reuse dynamic values
- **Version Control** — Publish changes when you're ready

### 🎯 Customer Data Platform

Build and manage your audience segments:

- Create targeted audiences based on user behavior
- Update segmentation rules on the fly

### ⚙️ Configuration & Settings

Fine-tune your Piwik PRO setup:

- **App Management** — Organize your sites and apps
- **Tracker Settings** — Configure tracking behavior globally or per-app
- **Container Settings** — Access installation code and container configuration

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

You're all set! The server starts in **safe mode** by default, so you can freely explore your analytics data without worrying about accidental changes.

Try these prompts to get started:

```
List my Piwik PRO apps.

List tags of <NAME> app.

What were the top 10 pages last week?

Show me conversion trends for the past month.
```

### Ready to Make Changes?

Once you're comfortable, disable safe mode to unlock create, update, and delete operations:

```
PIWIK_PRO_SAFE_MODE=0
```

Then try prompts like:

```
In app <NAME>, add a new tag that will show alert("hello") when user enters any page.

Copy tag <NAME> from app <APP> to all apps with <PREFIX> prefix.
```

### Other Options

- `PIWIK_PRO_TELEMETRY` (default `1`): Controls anonymous usage telemetry. Set to `0` to disable.
- `PIWIK_PRO_TM_RESOURCE_CHECK` (default `1`): Enables Tag Manager template validation. Set to `0` to bypass when experimenting with custom templates.

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

## 📚 Documentation

| Document                                 | Description                               |
| ---------------------------------------- | ----------------------------------------- |
| [Available Tools](docs/TOOLS.md)         | Complete reference of all MCP tools       |
| [Development Guide](docs/DEVELOPMENT.md) | Setup, running, testing, and architecture |
| [Contributing](CONTRIBUTION.md)          | How to contribute to the project          |
