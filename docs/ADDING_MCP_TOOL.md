# Adding a New MCP Tool

This guide explains how to add new MCP tools to the Piwik PRO MCP Server. The project follows a modular architecture that makes it easy to contribute new functionality.

## Table of Contents

- [Quick Start](#quick-start)
- [Architecture Overview](#architecture-overview)
- [Step-by-Step Guide](#step-by-step-guide)
- [Code Standards](#code-standards)
- [Testing](#testing)

## Quick Start

To add a new MCP tool from a different Piwik module, you need to:

1. **Add API client** - Create the API client in `src/piwik_pro_mcp/api/methods/`
2. **Create MCP tools** - Implement MCP tools in `src/piwik_pro_mcp/tools/`
3. **Register tools** - Add tool registration to the MCP server
4. **Add tests** - Write tests for your new functionality
5. **Update schemas** - Add parameter schemas if using JSON attributes
6. **Update EXPECTED_TOOLS** - Add new tool names to integration test list

## Architecture Overview

The project uses a unified architecture with the API client integrated within the MCP module:

```
src/piwik_pro_mcp/
├── api/                    # API client library
│   ├── client.py           # Main HTTP client with OAuth2 authentication
│   ├── auth.py             # Client credentials flow implementation
│   ├── config.py           # Configuration management
│   ├── exceptions.py       # Custom exception hierarchy (NotFoundError, BadRequestError, etc.)
│   └── methods/            # API endpoint implementations
│       └── your_module/    # Your new API module
│           ├── api.py      # API implementation
│           └── models.py   # Pydantic data models
├── tools/                  # MCP tool implementations
│   └── your_module/        # Your new MCP tools
│       ├── tools.py        # MCP tool implementations
│       └── models.py       # MCP response models (optional)
├── common/                 # Shared utilities
│   ├── utils.py            # create_piwik_client, validate_data_against_model
│   └── tool_schemas.py     # Tool parameter schema mappings
├── responses.py            # Shared MCP response models
└── tests/                  # Test suite
    └── test_integration.py # Integration tests with EXPECTED_TOOLS list
```

## Step-by-Step Guide

### Step 1: Create the API Client

First, create the API client in the integrated API structure:

#### 1.1 Create the API module directory

```bash
mkdir -p src/piwik_pro_mcp/api/methods/your_module
touch src/piwik_pro_mcp/api/methods/your_module/__init__.py
```

#### 1.2 Define data models (`src/piwik_pro_mcp/api/methods/your_module/models.py`)

```python
"""
Data models for Your Module API.
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class YourResourceType(str, Enum):
    """Enum for resource types."""
    TYPE_A = "type_a"
    TYPE_B = "type_b"


class YourResource(BaseModel):
    """Your resource model."""
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(description="Resource ID")
    name: str = Field(description="Resource name")
    resource_type: YourResourceType = Field(alias="resourceType", description="Resource type")
    created_at: Optional[str] = Field(alias="createdAt", description="Creation timestamp")


class NewYourResourceAttributes(BaseModel):
    """Attributes for creating a new resource."""
    name: str = Field(max_length=255, description="Resource name")
    resource_type: YourResourceType = Field(description="Resource type")


class YourResourceEditableAttributes(BaseModel):
    """Attributes for updating a resource."""
    name: Optional[str] = Field(None, max_length=255, description="Resource name")
    resource_type: Optional[YourResourceType] = Field(None, description="Resource type")
```

#### 1.3 Implement the API client (`src/piwik_pro_mcp/api/methods/your_module/api.py`)

```python
"""
Your Module API for Piwik PRO.
"""

from typing import TYPE_CHECKING, Any, Dict, Optional, Union

if TYPE_CHECKING:
    from ...client import PiwikProClient
from .models import (
    NewYourResourceAttributes,
    YourResourceEditableAttributes,
)


class YourModuleAPI:
    """Your Module API client for Piwik PRO."""

    def __init__(self, client: "PiwikProClient"):
        self.client = client

    def list_resources(
        self,
        app_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Union[Dict[str, Any], None]:
        """List resources for an app."""
        params = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset

        return self.client.get(f"/api/apps/v2/{app_id}/your-module/resources", params=params)

    def get_resource(self, app_id: str, resource_id: str) -> Union[Dict[str, Any], None]:
        """Get a specific resource."""
        return self.client.get(f"/api/apps/v2/{app_id}/your-module/resources/{resource_id}")

    def create_resource(
        self,
        app_id: str,
        attributes: NewYourResourceAttributes,
    ) -> Union[Dict[str, Any], None]:
        """Create a new resource."""
        data = attributes.model_dump(exclude_none=True, by_alias=True)
        return self.client.post(f"/api/apps/v2/{app_id}/your-module/resources", json=data)

    def update_resource(
        self,
        app_id: str,
        resource_id: str,
        attributes: YourResourceEditableAttributes,
    ) -> Union[Dict[str, Any], None]:
        """Update a resource."""
        data = attributes.model_dump(exclude_none=True, by_alias=True)
        return self.client.patch(f"/api/apps/v2/{app_id}/your-module/resources/{resource_id}", json=data)

    def delete_resource(self, app_id: str, resource_id: str) -> Union[Dict[str, Any], None]:
        """Delete a resource. Returns None for successful deletion (204 response)."""
        return self.client.delete(f"/api/apps/v2/{app_id}/your-module/resources/{resource_id}")
```

#### 1.4 Create module exports (`src/piwik_pro_mcp/api/methods/your_module/__init__.py`)

```python
"""Your Module API exports."""

from .api import YourModuleAPI
from .models import (
    NewYourResourceAttributes,
    YourResource,
    YourResourceEditableAttributes,
    YourResourceType,
)

__all__ = [
    "YourModuleAPI",
    "YourResource",
    "YourResourceType",
    "NewYourResourceAttributes",
    "YourResourceEditableAttributes",
]
```

#### 1.5 Add to main API client (`src/piwik_pro_mcp/api/client.py`)

```python
# In the imports section
from .methods.your_module import YourModuleAPI

# In the PiwikProClient class __init__ method
def __init__(self, ...):
    # ... existing code ...
    self.your_module = YourModuleAPI(self)
```

### Step 2: Create MCP Tools

Now create the MCP tools that use your API client:

#### 2.1 Create MCP tools directory

```bash
mkdir -p src/piwik_pro_mcp/tools/your_module
touch src/piwik_pro_mcp/tools/your_module/__init__.py
```

#### 2.2 Create MCP response models (optional) (`src/piwik_pro_mcp/tools/your_module/models.py`)

```python
"""MCP response models for Your Module tools."""

from typing import List
from pydantic import BaseModel, Field


class YourResourceSummary(BaseModel):
    """Summary of a resource for list responses."""
    id: str = Field(description="Resource ID")
    name: str = Field(description="Resource name")


class YourResourceListMCPResponse(BaseModel):
    """MCP response model for resource list."""
    resources: List[YourResourceSummary] = Field(description="List of resources")
    total: int = Field(description="Total number of resources")
    limit: int = Field(description="Number of resources requested")
    offset: int = Field(description="Number of resources skipped")


class YourResourceDetailsMCPResponse(BaseModel):
    """MCP response model for resource details."""
    id: str = Field(description="Resource ID")
    name: str = Field(description="Resource name")
    resource_type: str = Field(description="Resource type")
    created_at: str = Field(description="Creation timestamp")
```

#### 2.3 Implement MCP tools (`src/piwik_pro_mcp/tools/your_module/tools.py`)

**Important conventions:**

- Tool names use `{module}_{operation}` pattern (e.g., `resources_list`, NOT `piwik_resources_list`)
- Use `@mcp.tool(annotations={"readOnlyHint": True})` for read-only tools (required for safe mode)
- Use `validate_data_against_model` for JSON attribute validation
- Catch specific exceptions (`NotFoundError`, `BadRequestError`) for better error messages
- Use shared response models from `responses.py` (`OperationStatusResponse`, `UpdateStatusResponse`)

```python
"""Your Module MCP tools implementation."""

from typing import Optional
from mcp.server.fastmcp import FastMCP

from piwik_pro_mcp.api.exceptions import BadRequestError, NotFoundError
from piwik_pro_mcp.api.methods.your_module.models import (
    NewYourResourceAttributes,
    YourResourceEditableAttributes,
)

from ...common.utils import create_piwik_client, validate_data_against_model
from ...responses import OperationStatusResponse, UpdateStatusResponse
from .models import (
    YourResourceDetailsMCPResponse,
    YourResourceListMCPResponse,
    YourResourceSummary,
)


# --- Implementation functions ---

def list_resources(app_id: str, limit: int = 10, offset: int = 0) -> YourResourceListMCPResponse:
    """List resources for an app."""
    try:
        client = create_piwik_client()
        response = client.your_module.list_resources(app_id=app_id, limit=limit, offset=offset)

        resources = [
            YourResourceSummary(id=r["id"], name=r["attributes"]["name"])
            for r in response.get("data", [])
        ]

        return YourResourceListMCPResponse(
            resources=resources,
            total=response.get("meta", {}).get("total", 0),
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        raise RuntimeError(f"Failed to list resources: {str(e)}")


def get_resource_details(app_id: str, resource_id: str) -> YourResourceDetailsMCPResponse:
    """Get detailed information about a specific resource."""
    try:
        client = create_piwik_client()
        response = client.your_module.get_resource(app_id, resource_id)

        data = response["data"]
        attrs = data["attributes"]

        return YourResourceDetailsMCPResponse(
            id=data["id"],
            name=attrs["name"],
            resource_type=attrs["resourceType"],
            created_at=attrs.get("createdAt", ""),
        )
    except NotFoundError:
        raise RuntimeError(f"Resource with ID {resource_id} not found")
    except Exception as e:
        raise RuntimeError(f"Failed to get resource details: {str(e)}")


def create_resource(app_id: str, attributes: dict) -> YourResourceDetailsMCPResponse:
    """Create a new resource."""
    try:
        client = create_piwik_client()

        # Validate attributes against the model
        validated_attrs = validate_data_against_model(attributes, NewYourResourceAttributes)

        response = client.your_module.create_resource(app_id, validated_attrs)

        data = response["data"]
        attrs = data["attributes"]

        return YourResourceDetailsMCPResponse(
            id=data["id"],
            name=attrs["name"],
            resource_type=attrs["resourceType"],
            created_at=attrs.get("createdAt", ""),
        )
    except BadRequestError as e:
        raise RuntimeError(f"Failed to create resource: {e.message}")
    except Exception as e:
        raise RuntimeError(f"Failed to create resource: {str(e)}")


def update_resource(app_id: str, resource_id: str, attributes: dict) -> UpdateStatusResponse:
    """Update a resource."""
    try:
        client = create_piwik_client()

        # Validate attributes against the model
        validated_attrs = validate_data_against_model(attributes, YourResourceEditableAttributes)

        # Convert to dictionary and filter out None values
        update_kwargs = {
            k: v for k, v in validated_attrs.model_dump(by_alias=True, exclude_none=True).items()
        }

        if not update_kwargs:
            raise RuntimeError("No update parameters provided")

        updated_fields = list(update_kwargs.keys())
        client.your_module.update_resource(app_id, resource_id, validated_attrs)

        return UpdateStatusResponse(
            status="success",
            message=f"Resource {resource_id} updated successfully",
            updated_fields=updated_fields,
        )
    except NotFoundError:
        raise RuntimeError(f"Resource with ID {resource_id} not found")
    except BadRequestError as e:
        raise RuntimeError(f"Failed to update resource: {e.message}")
    except Exception as e:
        raise RuntimeError(f"Failed to update resource: {str(e)}")


def delete_resource(app_id: str, resource_id: str) -> OperationStatusResponse:
    """Delete a resource."""
    try:
        client = create_piwik_client()
        client.your_module.delete_resource(app_id, resource_id)

        return OperationStatusResponse(
            status="success",
            message=f"Resource {resource_id} deleted successfully",
        )
    except NotFoundError:
        raise RuntimeError(f"Resource with ID {resource_id} not found")
    except BadRequestError as e:
        raise RuntimeError(f"Failed to delete resource: {e.message}")
    except Exception as e:
        raise RuntimeError(f"Failed to delete resource: {str(e)}")


# --- Tool registration ---

def register_your_module_tools(mcp: FastMCP) -> None:
    """Register all Your Module tools with the MCP server."""

    # READ-ONLY TOOLS - use readOnlyHint annotation for safe mode support
    @mcp.tool(annotations={"title": "Piwik PRO: List Resources", "readOnlyHint": True})
    def resources_list(
        app_id: str,
        limit: int = 10,
        offset: int = 0,
    ) -> YourResourceListMCPResponse:
        """List resources for a Piwik PRO app.

        Args:
            app_id: UUID of the app
            limit: Maximum number of resources to return (default: 10)
            offset: Number of resources to skip (default: 0)

        Returns:
            List of resources with metadata
        """
        return list_resources(app_id=app_id, limit=limit, offset=offset)

    @mcp.tool(annotations={"title": "Piwik PRO: Get Resource", "readOnlyHint": True})
    def resources_get(app_id: str, resource_id: str) -> YourResourceDetailsMCPResponse:
        """Get detailed information about a specific resource.

        Args:
            app_id: UUID of the app
            resource_id: ID of the resource to retrieve

        Returns:
            Detailed resource information
        """
        return get_resource_details(app_id, resource_id)

    # WRITE TOOLS - no readOnlyHint (disabled in safe mode)
    @mcp.tool(annotations={"title": "Piwik PRO: Create Resource"})
    def resources_create(app_id: str, attributes: dict) -> YourResourceDetailsMCPResponse:
        """Create a new resource using JSON attributes.

        Use tools_parameters_get("resources_create") to get the complete
        JSON schema with all available fields, types, and validation rules.

        Args:
            app_id: UUID of the app
            attributes: Dictionary containing resource attributes.
                        Required: name, resource_type

        Returns:
            Created resource details

        Examples:
            attributes = {
                "name": "My Resource",
                "resource_type": "type_a"
            }
        """
        return create_resource(app_id=app_id, attributes=attributes)

    @mcp.tool(annotations={"title": "Piwik PRO: Update Resource"})
    def resources_update(
        app_id: str,
        resource_id: str,
        attributes: dict,
    ) -> UpdateStatusResponse:
        """Update a resource using JSON attributes.

        Use tools_parameters_get("resources_update") to get the complete
        JSON schema with all available fields.

        Args:
            app_id: UUID of the app
            resource_id: ID of the resource to update
            attributes: Dictionary containing attributes to update (all optional)

        Returns:
            Update status with list of updated fields
        """
        return update_resource(app_id=app_id, resource_id=resource_id, attributes=attributes)

    @mcp.tool(annotations={"title": "Piwik PRO: Delete Resource"})
    def resources_delete(app_id: str, resource_id: str) -> OperationStatusResponse:
        """Delete a resource.

        Args:
            app_id: UUID of the app
            resource_id: ID of the resource to delete

        Returns:
            Operation status
        """
        return delete_resource(app_id=app_id, resource_id=resource_id)
```

#### 2.4 Create module exports (`src/piwik_pro_mcp/tools/your_module/__init__.py`)

Only export the registration function:

```python
"""Your Module tools for Piwik PRO MCP server."""

from .tools import register_your_module_tools

__all__ = [
    "register_your_module_tools",
]
```

### Step 3: Register Tools with MCP Server

#### 3.1 Add to tool registration (`src/piwik_pro_mcp/tools/__init__.py`)

```python
# Add import
from .your_module import register_your_module_tools

# Add to register_all_tools function
def register_all_tools(mcp: FastMCP) -> None:
    """Register all MCP tools with the server."""
    # ... existing registrations ...

    # Register your module tools
    register_your_module_tools(mcp)

# Add to __all__ list
__all__ = [
    "register_all_tools",
    "filter_write_tools",
    # ... existing exports ...
    "register_your_module_tools",
]
```

#### 3.2 Add parameter schemas (`src/piwik_pro_mcp/common/tool_schemas.py`)

If your tools accept JSON attributes, add them to the schema mapping:

```python
# Add imports
from piwik_pro_mcp.api.methods.your_module.models import (
    NewYourResourceAttributes,
    YourResourceEditableAttributes,
)

# Add to TOOL_PARAMETER_MODELS dictionary
TOOL_PARAMETER_MODELS: Dict[str, Type[BaseModel]] = {
    # ... existing mappings ...
    "resources_create": NewYourResourceAttributes,
    "resources_update": YourResourceEditableAttributes,
}
```

### Step 4: Add Tests

#### 4.1 Update integration test (`src/piwik_pro_mcp/tests/test_integration.py`)

**Important:** You must add your new tool names to the `EXPECTED_TOOLS` list. The integration test validates that the exact set of expected tools exists.

```python
class TestMCPToolsExist:
    EXPECTED_TOOLS = [
        # ... existing tools ...
        # Your Module Tools
        "resources_list",
        "resources_get",
        "resources_create",
        "resources_update",
        "resources_delete",
    ]
```

#### 4.2 Create unit tests (`src/piwik_pro_mcp/tests/tools/your_module/test_tools.py`)

```python
"""Tests for Your Module MCP tools."""

import pytest
from unittest.mock import Mock, patch

from piwik_pro_mcp.tools.your_module.tools import (
    create_resource,
    delete_resource,
    get_resource_details,
    list_resources,
    update_resource,
)


class TestYourModuleTools:
    """Test Your Module MCP tools."""

    @patch("piwik_pro_mcp.tools.your_module.tools.create_piwik_client")
    def test_list_resources_success(self, mock_create_client):
        """Test successful resource listing."""
        mock_client = Mock()
        mock_client.your_module.list_resources.return_value = {
            "data": [{"id": "res-1", "attributes": {"name": "Test Resource"}}],
            "meta": {"total": 1},
        }
        mock_create_client.return_value = mock_client

        result = list_resources("app-123", limit=10, offset=0)

        assert result.total == 1
        assert len(result.resources) == 1
        assert result.resources[0].name == "Test Resource"

    @patch("piwik_pro_mcp.tools.your_module.tools.create_piwik_client")
    def test_create_resource_success(self, mock_create_client):
        """Test successful resource creation."""
        mock_client = Mock()
        mock_client.your_module.create_resource.return_value = {
            "data": {
                "id": "new-res",
                "attributes": {
                    "name": "New Resource",
                    "resourceType": "type_a",
                    "createdAt": "2024-01-01T00:00:00Z",
                },
            },
        }
        mock_create_client.return_value = mock_client

        result = create_resource("app-123", {"name": "New Resource", "resource_type": "type_a"})

        assert result.id == "new-res"
        assert result.name == "New Resource"
```

### Step 5: Run Tests and Quality Checks

```bash
# Install dependencies
uv sync --dev

# Run your module's tests
uv run pytest src/piwik_pro_mcp/tests/tools/your_module/ -v

# Run integration tests (verifies EXPECTED_TOOLS)
uv run pytest src/piwik_pro_mcp/tests/test_integration.py -v

# Check code quality
uv run ruff check .
uv run ruff format .

# Run all tests with coverage
uv run pytest --cov=piwik_pro_mcp
```

## Code Standards

### Tool Naming Convention

Tools use the `{module}_{operation}` naming pattern:

| Pattern           | Examples                                         |
| ----------------- | ------------------------------------------------ |
| `{module}_list`   | `apps_list`, `tags_list`, `audiences_list`       |
| `{module}_get`    | `apps_get`, `tags_get`, `triggers_get`           |
| `{module}_create` | `apps_create`, `tags_create`, `variables_create` |
| `{module}_update` | `apps_update`, `tags_update`, `audiences_update` |
| `{module}_delete` | `apps_delete`, `tags_delete`, `triggers_delete`  |

**Do NOT** prefix tools with `piwik_`.

### Tool Annotations (Safe Mode Support)

The server supports a safe mode that only exposes read-only tools. Mark your tools appropriately:

```python
# Read-only tools - MUST have readOnlyHint: True
@mcp.tool(annotations={"title": "Piwik PRO: List Resources", "readOnlyHint": True})
def resources_list(...):
    ...

# Write tools - no readOnlyHint (or explicitly False)
@mcp.tool(annotations={"title": "Piwik PRO: Create Resource"})
def resources_create(...):
    ...
```

### Error Handling

Catch specific exceptions for better error messages:

```python
from piwik_pro_mcp.api.exceptions import BadRequestError, NotFoundError

try:
    client.your_module.get_resource(app_id, resource_id)
except NotFoundError:
    raise RuntimeError(f"Resource with ID {resource_id} not found")
except BadRequestError as e:
    raise RuntimeError(f"Failed to get resource: {e.message}")
except Exception as e:
    raise RuntimeError(f"Failed to get resource: {str(e)}")
```

### Attribute Validation

Use `validate_data_against_model` for JSON attribute validation:

```python
from ...common.utils import validate_data_against_model

def create_resource(app_id: str, attributes: dict) -> ...:
    # Validates and returns a typed Pydantic model
    validated_attrs = validate_data_against_model(attributes, NewYourResourceAttributes)

    # Use the validated model
    response = client.your_module.create_resource(app_id, validated_attrs)
```

### Response Models

Use shared response models from `responses.py`:

| Model                     | Use Case                                           |
| ------------------------- | -------------------------------------------------- |
| `OperationStatusResponse` | Delete operations, simple success/failure          |
| `UpdateStatusResponse`    | Update operations (includes `updated_fields` list) |
| `CopyResourceResponse`    | Copy operations (tags, triggers, variables)        |

### Import Organization

- **All imports at the top of files** - Never use imports inside functions
- Standard library imports first
- Third-party imports second
- Local imports last

```python
# Standard library
from typing import Optional

# Third-party
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# Local - API exceptions and models
from piwik_pro_mcp.api.exceptions import BadRequestError, NotFoundError
from piwik_pro_mcp.api.methods.your_module.models import NewYourResourceAttributes

# Local - common utilities
from ...common.utils import create_piwik_client, validate_data_against_model
from ...responses import OperationStatusResponse
```

### Type Hints and Documentation

- Always use type hints for function parameters and return types
- Use Google-style docstrings with Args, Returns, and Raises sections
- Use `Optional[T]` for nullable parameters

## Testing

### Test Organization

- **Framework**: pytest with pytest-cov for coverage
- **Command**: Always use `uv run pytest` - never `pytest` directly
- **Mocking**: Use `unittest.mock` for external dependencies

### Integration Test Requirement

When adding new tools, you **must** update the `EXPECTED_TOOLS` list in `src/piwik_pro_mcp/tests/test_integration.py`. The test validates that exactly the expected set of tools exists:

```python
class TestMCPToolsExist:
    EXPECTED_TOOLS = [
        # Add your tools here
        "resources_list",
        "resources_get",
        "resources_create",
        "resources_update",
        "resources_delete",
    ]
```

If you forget to add your tools, the integration test will fail with a message showing the difference between expected and actual tools.

## Common Pitfalls

1. **Wrong tool naming** - Use `module_operation`, not `piwik_module_operation`
2. **Missing readOnlyHint** - Read-only tools must have `readOnlyHint: True` for safe mode
3. **Missing EXPECTED_TOOLS entry** - Always add new tools to the integration test list
4. **Missing parameter schema** - Add to `tool_schemas.py` for JSON attribute tools
5. **Imports inside functions** - Always import at the top of files
6. **Generic error handling** - Catch specific exceptions (`NotFoundError`, `BadRequestError`)
7. **Missing attribute validation** - Use `validate_data_against_model` for JSON attributes
8. **Not using `uv run`** - Always use `uv run pytest`, never `pytest` directly

## Getting Help

- Check existing modules for patterns (apps, tag_manager, analytics)
- Review `CLAUDE.md` for detailed coding standards
- Look at test files for testing patterns
- Ask questions in pull request reviews

## Summary

Adding a new MCP tool module involves:

1. **API Client**: Create models and API client in `src/piwik_pro_mcp/api/methods/your_module/`
2. **MCP Tools**: Implement tools in `src/piwik_pro_mcp/tools/your_module/`
   - Use `{module}_{operation}` naming (e.g., `resources_list`)
   - Add `readOnlyHint: True` annotation for read-only tools
   - Use `validate_data_against_model` for attribute validation
   - Catch specific exceptions for better error messages
3. **Registration**: Add to `src/piwik_pro_mcp/tools/__init__.py`
4. **Schemas**: Add parameter schemas to `src/piwik_pro_mcp/common/tool_schemas.py`
5. **Tests**:
   - Add tool names to `EXPECTED_TOOLS` in integration test
   - Write unit tests for your tools
6. **Quality**: Run linting, formatting, and all tests
