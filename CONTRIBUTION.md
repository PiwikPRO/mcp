# Contributing to Piwik PRO MCP Server

Thank you for your interest in contributing! This document will help you get started.

## Documentation

| Document                                         | Description                               |
| ------------------------------------------------ | ----------------------------------------- |
| [Development Guide](docs/DEVELOPMENT.md)         | Setup, running, testing, and architecture |
| [Adding a New MCP Tool](docs/ADDING_MCP_TOOL.md) | Step-by-step guide for adding new tools   |
| [Available Tools](docs/TOOLS.md)                 | Complete reference of all MCP tools       |

## Quick Links

- **Setting up the project?** Start with the [Development Guide](docs/DEVELOPMENT.md)
- **Adding a new tool?** Follow the [Adding a New MCP Tool](docs/ADDING_MCP_TOOL.md) guide
- **Looking for tool documentation?** Check [Available Tools](docs/TOOLS.md)

## Contribution Process

1. **Fork the repository** and create your branch from `master`
2. **Set up the development environment** following the [Development Guide](docs/DEVELOPMENT.md)
3. **Make your changes** following the patterns in [Adding a New MCP Tool](docs/ADDING_MCP_TOOL.md)
4. **Write tests** for any new functionality
5. **Run quality checks**:
   ```bash
   uv run ruff check .
   uv run ruff format .
   uv run pytest
   ```
6. **Submit a pull request** with a clear description of your changes

## Code Style

- Python 3.12+
- Ruff for linting and formatting (120 char line length)
- Google-style docstrings
- Full type annotations with Pydantic models
- All imports at the top of files

## Getting Help

- Check existing modules for patterns (apps, tag_manager, analytics)
- Review the [Development Guide](docs/DEVELOPMENT.md) for architecture details
- Open an issue for questions or discussions
