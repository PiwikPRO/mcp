# Contributing to Piwik PRO MCP Server

This guide explains how to add new MCP tools to the Piwik PRO MCP Server. The project follows a modular architecture that makes it easy to contribute new functionality.

## Table of Contents

- [Quick Start](#quick-start)
- [Architecture Overview](#architecture-overview)
- [Step-by-Step Guide](#step-by-step-guide)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Examples](#examples)

## Quick Start

To add a new MCP tool from a different Piwik module, you need to:

1. **Add API client** - Create the API client in `src/piwik_pro_mcp/api/methods/`
2. **Create MCP tools** - Implement MCP tools in `src/piwik_pro_mcp/tools/`
3. **Register tools** - Add tool registration to the MCP server
4. **Add tests** - Write tests for your new functionality
5. **Update schemas** - Add parameter schemas if using JSON attributes

## Architecture Overview

The project uses a unified architecture with the API client integrated within the MCP module:

```
src/piwik_pro_mcp/      # Main MCP server implementation with integrated API client
├── api/                # Complete API client library (integrated within MCP module)
│   ├── client.py       # Main HTTP client with OAuth2 authentication
│   ├── auth.py         # Client credentials flow implementation
│   ├── config.py       # Configuration management
│   ├── exceptions.py   # Custom exception hierarchy
│   └── methods/        # API endpoint implementations
│       ├── common.py   # Shared API functionality
│       └── your_module/ # Your new API module
│           ├── api.py   # API implementation
│           └── models.py # Pydantic data models
├── tools/              # Organized MCP tool implementations
│   └── your_module/    # Your new MCP tools
│       ├── tools.py    # MCP tool implementations
│       └── models.py   # MCP-specific models (optional)
├── common/             # Shared utilities and schemas
│   ├── utils.py        # Shared utility functions
│   └── tool_schemas.py # Common tool schema definitions
└── assets/             # Template assets and examples
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

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

if TYPE_CHECKING:
    from ...client import PiwikProClient
from .models import (
    NewYourResourceAttributes,
    YourResource,
    YourResourceEditableAttributes,
)


class YourModuleAPI:
    """Your Module API client for Piwik PRO."""

    def __init__(self, client: "PiwikProClient"):
        """
        Initialize Your Module API client.

        Args:
            client: Piwik PRO HTTP client instance
        """
        self.client = client

    def list_resources(
        self,
        app_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Union[Dict[str, Any], None]:
        """
        List resources for an app.

        Args:
            app_id: App ID
            limit: Maximum number of items to return
            offset: Number of items to skip

        Returns:
            Dictionary containing resources list and metadata
        """
        params = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset

        return self.client.get(f"/api/apps/v2/{app_id}/your-module/resources", params=params)

    def get_resource(self, app_id: str, resource_id: str) -> Union[Dict[str, Any], None]:
        """
        Get a specific resource.

        Args:
            app_id: App ID
            resource_id: Resource ID

        Returns:
            Dictionary containing resource details
        """
        return self.client.get(f"/api/apps/v2/{app_id}/your-module/resources/{resource_id}")

    def create_resource(
        self,
        app_id: str,
        attributes: NewYourResourceAttributes,
    ) -> Union[Dict[str, Any], None]:
        """
        Create a new resource.

        Args:
            app_id: App ID
            attributes: Resource attributes

        Returns:
            Dictionary containing created resource details
        """
        data = attributes.model_dump(exclude_none=True, by_alias=True)
        return self.client.post(f"/api/apps/v2/{app_id}/your-module/resources", json=data)

    def update_resource(
        self,
        app_id: str,
        resource_id: str,
        attributes: YourResourceEditableAttributes,
    ) -> Union[Dict[str, Any], None]:
        """
        Update a resource.

        Args:
            app_id: App ID
            resource_id: Resource ID
            attributes: Resource attributes to update

        Returns:
            Dictionary containing updated resource details
        """
        data = attributes.model_dump(exclude_none=True, by_alias=True)
        return self.client.patch(f"/api/apps/v2/{app_id}/your-module/resources/{resource_id}", json=data)

    def delete_resource(self, app_id: str, resource_id: str) -> Union[Dict[str, Any], None]:
        """
        Delete a resource.

        Args:
            app_id: App ID
            resource_id: Resource ID

        Returns:
            None for successful deletion (204 response)
        """
        return self.client.delete(f"/api/apps/v2/{app_id}/your-module/resources/{resource_id}")
```

#### 1.4 Create module exports (`src/piwik_pro_mcp/api/methods/your_module/__init__.py`)

```python
"""
Your Module API exports.
"""

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

Add your API to the main client:

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
"""
MCP-specific models for Your Module tools.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

from ...api.methods.your_module.models import (
    NewYourResourceAttributes,
    YourResourceEditableAttributes,
)


class YourResourceListMCPResponse(BaseModel):
    """MCP response model for resource list."""
    resources: List[dict] = Field(description="List of resources")
    total: int = Field(description="Total number of resources")
    limit: int = Field(description="Number of resources requested")
    offset: int = Field(description="Number of resources skipped")


class YourResourceDetailsMCPResponse(BaseModel):
    """MCP response model for resource details."""
    resource: dict = Field(description="Resource details")


# Re-export API models for convenience
YourResourceCreateMCPRequest = NewYourResourceAttributes
YourResourceUpdateMCPRequest = YourResourceEditableAttributes
```

#### 2.3 Implement MCP tools (`src/piwik_pro_mcp/tools/your_module/tools.py`)

```python
"""
Your Module MCP tools implementation.
"""

from typing import Optional
from mcp.server.fastmcp import FastMCP

from ...common.utils import create_piwik_client, validate_app_id
from ...responses import OperationStatusResponse
from ...api.methods.your_module.models import (
    NewYourResourceAttributes,
    YourResourceEditableAttributes,
)

from .models import (
    YourResourceDetailsMCPResponse,
    YourResourceListMCPResponse,
)


def list_resources(app_id: str, limit: int = 10, offset: int = 0) -> YourResourceListMCPResponse:
    """
    List resources for an app.

    Args:
        app_id: App ID
        limit: Maximum number of resources to return
        offset: Number of resources to skip

    Returns:
        YourResourceListMCPResponse with resources list and metadata

    Raises:
        RuntimeError: If the API request fails
    """
    try:
        validate_app_id(app_id)
        client = create_piwik_client()
        
        response = client.your_module.list_resources(
            app_id=app_id,
            limit=limit,
            offset=offset,
        )
        
        return YourResourceListMCPResponse(
            resources=response.get("data", []),
            total=response.get("meta", {}).get("total", 0),
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        raise RuntimeError(f"Failed to list resources: {str(e)}")


def get_resource_details(app_id: str, resource_id: str) -> YourResourceDetailsMCPResponse:
    """
    Get detailed information about a specific resource.

    Args:
        app_id: App ID
        resource_id: Resource ID

    Returns:
        YourResourceDetailsMCPResponse with resource details

    Raises:
        RuntimeError: If the API request fails
    """
    try:
        validate_app_id(app_id)
        client = create_piwik_client()
        
        response = client.your_module.get_resource(app_id, resource_id)
        
        return YourResourceDetailsMCPResponse(resource=response)
    except Exception as e:
        raise RuntimeError(f"Failed to get resource details: {str(e)}")


def create_resource(app_id: str, attributes: dict) -> YourResourceDetailsMCPResponse:
    """
    Create a new resource.

    Args:
        app_id: App ID
        attributes: Resource attributes dictionary

    Returns:
        YourResourceDetailsMCPResponse with created resource details

    Raises:
        RuntimeError: If the API request fails
    """
    try:
        validate_app_id(app_id)
        client = create_piwik_client()
        
        # Validate and parse attributes
        resource_attrs = NewYourResourceAttributes.model_validate(attributes)
        
        response = client.your_module.create_resource(app_id, resource_attrs)
        
        return YourResourceDetailsMCPResponse(resource=response)
    except Exception as e:
        raise RuntimeError(f"Failed to create resource: {str(e)}")


def update_resource(app_id: str, resource_id: str, attributes: dict) -> YourResourceDetailsMCPResponse:
    """
    Update a resource.

    Args:
        app_id: App ID
        resource_id: Resource ID
        attributes: Resource attributes dictionary

    Returns:
        YourResourceDetailsMCPResponse with updated resource details

    Raises:
        RuntimeError: If the API request fails
    """
    try:
        validate_app_id(app_id)
        client = create_piwik_client()
        
        # Validate and parse attributes
        resource_attrs = YourResourceEditableAttributes.model_validate(attributes)
        
        response = client.your_module.update_resource(app_id, resource_id, resource_attrs)
        
        return YourResourceDetailsMCPResponse(resource=response)
    except Exception as e:
        raise RuntimeError(f"Failed to update resource: {str(e)}")


def delete_resource(app_id: str, resource_id: str) -> OperationStatusResponse:
    """
    Delete a resource.

    Args:
        app_id: App ID
        resource_id: Resource ID

    Returns:
        OperationStatusResponse indicating success

    Raises:
        RuntimeError: If the API request fails
    """
    try:
        validate_app_id(app_id)
        client = create_piwik_client()
        
        client.your_module.delete_resource(app_id, resource_id)
        
        return OperationStatusResponse(
            status="success",
            message=f"Resource {resource_id} deleted successfully"
        )
    except Exception as e:
        raise RuntimeError(f"Failed to delete resource: {str(e)}")


def register_your_module_tools(mcp: FastMCP) -> None:
    """Register all Your Module tools with the MCP server."""

    @mcp.tool()
    def piwik_list_resources(
        app_id: str,
        limit: int = 10,
        offset: int = 0,
    ) -> YourResourceListMCPResponse:
        """List resources for a Piwik PRO app.

        Args:
            app_id: UUID of the app
            limit: Maximum number of resources to return (default: 10, max: 1000)
            offset: Number of resources to skip (default: 0)

        Returns:
            Dictionary containing resource list and metadata including:
            - resources: List of resource objects
            - total: Total number of resources available
            - limit: Number of resources requested
            - offset: Number of resources skipped
        """
        return list_resources(app_id=app_id, limit=limit, offset=offset)

    @mcp.tool()
    def piwik_get_resource(app_id: str, resource_id: str) -> YourResourceDetailsMCPResponse:
        """Get detailed information about a specific resource.

        Args:
            app_id: UUID of the app
            resource_id: ID of the resource to retrieve

        Returns:
            Dictionary containing detailed resource information
        """
        return get_resource_details(app_id, resource_id)

    @mcp.tool()
    def piwik_create_resource(app_id: str, attributes: dict) -> YourResourceDetailsMCPResponse:
        """Create a new resource using JSON attributes.

        This tool uses a simplified interface with a single `attributes` parameter.
        Use tools_parameters_get("piwik_create_resource") to get the complete 
        JSON schema with all available fields, types, and validation rules.

        Args:
            app_id: UUID of the app
            attributes: Dictionary containing resource attributes. Required fields include
                       name and resource_type.

        Returns:
            Dictionary containing created resource details

        Parameter Discovery:
            💡 TIP: Use tools_parameters_get("piwik_create_resource") to get
            the complete JSON schema for all available fields.

        Examples:
            # Create a basic resource
            attributes = {
                "name": "My Resource",
                "resource_type": "type_a"
            }
        """
        return create_resource(app_id=app_id, attributes=attributes)

    @mcp.tool()
    def piwik_update_resource(
        app_id: str,
        resource_id: str,
        attributes: dict,
    ) -> YourResourceDetailsMCPResponse:
        """Update a resource using JSON attributes.

        This tool uses a simplified interface with a single `attributes` parameter.
        Use tools_parameters_get("piwik_update_resource") to get the complete 
        JSON schema with all available fields, types, and validation rules.

        Args:
            app_id: UUID of the app
            resource_id: ID of the resource to update
            attributes: Dictionary containing resource attributes to update.
                       All fields are optional.

        Returns:
            Dictionary containing updated resource details

        Parameter Discovery:
            💡 TIP: Use tools_parameters_get("piwik_update_resource") to get
            the complete JSON schema for all available fields.

        Examples:
            # Update resource name
            attributes = {"name": "Updated Resource Name"}
        """
        return update_resource(app_id=app_id, resource_id=resource_id, attributes=attributes)

    @mcp.tool()
    def piwik_delete_resource(app_id: str, resource_id: str) -> OperationStatusResponse:
        """Delete a resource.

        Args:
            app_id: UUID of the app
            resource_id: ID of the resource to delete

        Returns:
            Dictionary containing deletion status and message
        """
        return delete_resource(app_id=app_id, resource_id=resource_id)
```

#### 2.4 Create module exports (`src/piwik_pro_mcp/tools/your_module/__init__.py`)

```python
"""
Your Module tools for Piwik PRO MCP server.

This module provides MCP tools for managing Your Module resources
including creation, updating, listing, and deletion.
"""

from .models import (
    YourResourceCreateMCPRequest,
    YourResourceUpdateMCPRequest,
)
from .tools import (
    create_resource,
    delete_resource,
    get_resource_details,
    list_resources,
    register_your_module_tools,
    update_resource,
)

__all__ = [
    # Tool registration
    "register_your_module_tools",
    # Implementation functions
    "list_resources",
    "get_resource_details",
    "create_resource",
    "update_resource",
    "delete_resource",
    # MCP-specific models
    "YourResourceCreateMCPRequest",
    "YourResourceUpdateMCPRequest",
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
    # ... existing exports ...
    "register_your_module_tools",
]
```

#### 3.2 Add parameter schemas (`src/piwik_pro_mcp/common/tool_schemas.py`)

If your tools use the JSON attributes pattern, add them to the schema mapping:

```python
# Add imports
from ...api.methods.your_module.models import (
    NewYourResourceAttributes,
    YourResourceEditableAttributes,
)

# Add to TOOL_PARAMETER_MODELS dictionary
TOOL_PARAMETER_MODELS: Dict[str, Type[BaseModel]] = {
    # ... existing mappings ...
    "piwik_create_resource": NewYourResourceAttributes,
    "piwik_update_resource": YourResourceEditableAttributes,
}
```

### Step 4: Add Tests

#### 4.1 Add integration test (`tests/test_integration.py`)

Add your tools to the integration test:

```python
# In TestMCPToolExistence class, add to the tool list
@pytest.mark.parametrize(
    "tool_name",
    [
        # ... existing tools ...
        "piwik_list_resources",
        "piwik_get_resource",
        "piwik_create_resource",
        "piwik_update_resource",
        "piwik_delete_resource",
    ],
)
def test_mcp_tool_exists(self, mcp_server, tool_name):
    # ... existing test implementation ...
```

#### 4.2 Create unit tests (`src/piwik_pro_mcp/tests/tools/your_module/test_your_module.py`)

```python
"""
Tests for Your Module MCP tools.
"""

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
        # Mock client
        mock_client = Mock()
        mock_client.your_module.list_resources.return_value = {
            "data": [{"id": "resource1", "name": "Test Resource"}],
            "meta": {"total": 1},
        }
        mock_create_client.return_value = mock_client

        # Call function
        result = list_resources("app-123", limit=10, offset=0)

        # Assertions
        assert result.total == 1
        assert len(result.resources) == 1
        assert result.resources[0]["name"] == "Test Resource"
        mock_client.your_module.list_resources.assert_called_once_with(
            app_id="app-123", limit=10, offset=0
        )

    @patch("piwik_pro_mcp.tools.your_module.tools.create_piwik_client")
    def test_create_resource_success(self, mock_create_client):
        """Test successful resource creation."""
        # Mock client
        mock_client = Mock()
        mock_client.your_module.create_resource.return_value = {
            "id": "new-resource",
            "name": "New Resource",
        }
        mock_create_client.return_value = mock_client

        # Call function
        attributes = {"name": "New Resource", "resource_type": "type_a"}
        result = create_resource("app-123", attributes)

        # Assertions
        assert result.resource["name"] == "New Resource"
        mock_client.your_module.create_resource.assert_called_once()
```

### Step 5: Run Tests and Quality Checks

```bash
# Install dependencies
uv sync --dev

# Run tests
uv run pytest src/piwik_pro_mcp/tests/tools/your_module/test_your_module.py -v

# Run integration tests
uv run pytest src/piwik_pro_mcp/tests/test_integration.py -v

# Check code quality
uv run ruff check .
uv run ruff format .
uv run mypy .

# Run all tests with coverage
uv run pytest --cov=piwik_pro_mcp
```

## Code Standards

### Import Organization [[memory:4847942]]

- **All imports at the top of files** - Never use imports inside functions
- Standard library imports first
- Third-party imports second  
- Local imports last
- **Avoid noqa comments** - Fix architecture instead of hiding issues

### Type Hints and Documentation

- **Always use type hints** for function parameters and return types
- Use **Google-style docstrings** with Args, Returns, and Raises sections
- Include comprehensive examples in MCP tool docstrings
- Use `Optional[T]` for nullable parameters
- Use `Dict[str, Any]` for API responses

### MCP Tool Patterns

- **Tool naming**: Prefix with `piwik_` (e.g., `piwik_list_resources`)
- **Error handling**: Wrap all exceptions in `RuntimeError` with descriptive messages
- **Parameter discovery**: Use `list_available_parameters` tool for JSON attributes
- **Related tools**: Document related tools in docstrings
- **Return types**: Use Pydantic models for structured responses

### Environment Variables

Required environment variables for development:

```bash
export PIWIK_PRO_HOST="your-instance.piwik.pro"
export PIWIK_PRO_CLIENT_ID="your-client-id"
export PIWIK_PRO_CLIENT_SECRET="your-client-secret"
```

## Testing

### Test Organization

- **Framework**: pytest with pytest-cov for coverage
- **Command**: ALWAYS use `uv run pytest` - never `pytest` directly
- **Mocking**: Use `unittest.mock` for external dependencies
- **Fixtures**: Use class-scoped fixtures for environment setup

### Test Examples

```bash
# Run all tests
uv run pytest

# Run specific module tests
uv run pytest tests/test_your_module.py

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=piwik_mcp --cov=piwik_pro_api
```

## Examples

### Complete Example: Analytics Reports Module

Here's a complete example of adding an Analytics Reports module:

1. **API Models** (`src/piwik_pro_mcp/api/methods/analytics/models.py`):

```python
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum

class ReportType(str, Enum):
    PAGES = "pages"
    EVENTS = "events"
    GOALS = "goals"

class ReportRequest(BaseModel):
    report_type: ReportType = Field(description="Type of report")
    date_from: str = Field(description="Start date (YYYY-MM-DD)")
    date_to: str = Field(description="End date (YYYY-MM-DD)")
    limit: Optional[int] = Field(None, description="Number of results")
```

2. **API Client** (`src/piwik_pro_mcp/api/methods/analytics/api.py`):

```python
class AnalyticsAPI:
    def __init__(self, client: "PiwikProClient"):
        self.client = client
    
    def get_report(self, app_id: str, request: ReportRequest) -> Dict[str, Any]:
        params = request.model_dump(exclude_none=True)
        return self.client.get(f"/api/analytics/v1/{app_id}/reports", params=params)
```

3. **MCP Tools** (`src/piwik_pro_mcp/tools/analytics/tools.py`):

```python
def register_analytics_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    def piwik_get_analytics_report(app_id: str, attributes: dict) -> dict:
        """Get analytics report using JSON attributes.
        
        Use tools_parameters_get("piwik_get_analytics_report") for schema.
        """
        return get_analytics_report(app_id, attributes)
```

4. **Registration** (update `src/piwik_pro_mcp/tools/__init__.py`):

```python
from .analytics import register_analytics_tools

def register_all_tools(mcp: FastMCP) -> None:
    # ... existing registrations ...
    register_analytics_tools(mcp)
```

5. **Schema Registration** (update `src/piwik_pro_mcp/common/tool_schemas.py`):

```python
TOOL_PARAMETER_MODELS: Dict[str, Type[BaseModel]] = {
    # ... existing mappings ...
    "piwik_get_analytics_report": ReportRequest,
}
```

## Common Pitfalls

1. **Don't put imports inside functions** [[memory:4847942]] - Always import at the top
2. **Don't use noqa comments** - Fix the underlying architecture issue
3. **Don't forget error handling** - Wrap exceptions in `RuntimeError`
4. **Don't skip parameter schemas** - Add to `tool_schemas.py` for JSON attributes tools
5. **Don't forget tests** - Add integration and unit tests
6. **Always use `uv run`** - Never use `python` or `pytest` directly

## Getting Help

- Check existing modules for patterns (apps, tag_manager, tracker_settings)
- Review the `.cursorrules` file for detailed coding standards
- Look at test files for testing patterns
- Ask questions in pull request reviews

## Summary

Adding a new MCP tool module involves:

1. ✅ **API Client**: Create models and API client in `src/piwik_pro_mcp/api/methods/your_module/`
2. ✅ **MCP Tools**: Implement MCP tools in `src/piwik_pro_mcp/tools/your_module/`
3. ✅ **Registration**: Add tool registration to `src/piwik_pro_mcp/tools/__init__.py`
4. ✅ **Schemas**: Add parameter schemas to `src/piwik_pro_mcp/common/tool_schemas.py`
5. ✅ **Tests**: Write unit and integration tests
6. ✅ **Quality**: Run linting, formatting, and type checking

The modular architecture makes it easy to add new functionality while maintaining clean separation of concerns and following established patterns.
