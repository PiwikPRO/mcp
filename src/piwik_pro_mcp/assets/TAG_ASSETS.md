# 🏗️ **Tag Manager Template System Architecture Guide**

## **🎯 Core Philosophy**

Our Tag Manager template system follows a **"pregenerated, AI-optimized documentation with field mutability"** approach rather than dynamic schema parsing. This provides:

- **Better control** over documentation quality and consistency
- **Clearer guidance** for both create and update operations
- **Simpler maintenance** with single source of truth per template
- **Field mutability awareness** - clearly distinguishing editable vs immutable fields
- **Unified templates** - one template serves both creation and editing workflows

## **📁 File Structure Pattern**

```
piwik_mcp/assets/tag_manager/
├── _common/
│   ├── tag_base.json           # Base for all the tags templates assets
│   ├── tag_base_ecommerce.json # Base for all the ecommerce tags templates assets
│   ├── trigger_base.json       # Base for all the triggers types assets
│   └── variable_base.json     # Base for all the variables types assets
├── tags/
│   ├── custom_tag.json         # Complete create/edit template
│   ├── google_analytics.json   # (future template)
│   ├── piwik.json              # (future template)
│   └── ...                     # (other templates)
├── triggers/
│   ├── click.json              # Complete create/edit template
│   ├── page_view.json          # Complete create/edit template
│   └── ...                     # (other templates)
└── variables/
    ├── constant.json           # Complete create/edit template
    ├── custom_javascript.json  # Complete create/edit template
    ├── dom_element.json        # Complete create/edit template
    ├── data_layer.json         # Complete create/edit template
    └── ...                     # (other templates)
```

**Key Principles**:

- **Filename = Template Name**: `custom_tag.json` → template name is `"custom_tag"`
- **Single Template, Dual Purpose**: Each template serves both create and update operations
- **Directory Registry**: Directory acts as template registry, no central index needed
- **Component Separation**: Tags, triggers, and variables in separate directories

### **Shared base (extends)**

To avoid repeating the same sections across many tag templates, shared content lives in **`tag_manager/_common/`**. A tag JSON can set `"extends": "tag_base"` so that at load time the loader deep-merges `_common/tag_base.json` with the template (template keys win). That way you only define template-specific parts in each file.

- **Base file**: `tag_manager/_common/tag_base.json` — contains `mcp_usage`, `required_attributes` (generic `name`, `template`), `optional_attributes` (e.g. `is_active`, `priority`, `consent_type`, `scheduler`), `read_only_attributes`, `trigger_management`, `field_mutability_guide`, `related_mcp_tools`, `triggers_troubleshooting`.
- **In a template**: Add `"extends": "tag_base"`, then only add `template_name`, `name_aliases`, `description`, `ai_usage_guide`, template-specific `required_attributes` (e.g. `code`, `template_options`) and any overrides, template-specific `optional_attributes`, `complete_examples`, `common_mistakes`, `troubleshooting`, and optional overrides to `field_mutability_guide` or `related_mcp_tools`.
- **Loader**: `get_tag_template()` uses `load_tag_template_with_extends()` so that extended templates are resolved before being returned; the `extends` key is removed from the result.
- **Variable references**: `variable_reference_fields` can be either a flat array of field paths or a mapping keyed by variant identifier when variable support depends on template variants.

The same pattern is used for **triggers** and **variables**:

- **Trigger base**: `_common/trigger_base.json` — shared `mcp_usage`, `required_attributes` (name, trigger_type, conditions), `read_only_attributes`, `field_mutability_guide`, `variable_reference_guide.getting_variable_ids`, `related_mcp_tools`, `workflow_example`. Trigger JSONs set `"extends": "trigger_base"` and add template-specific content. `get_trigger_template()` uses `load_trigger_template_with_extends()`.

- **Variable base**: `_common/variable_base.json` — shared `mcp_usage`, `required_attributes` (name, template), `optional_attributes` (options), `read_only_attributes`, `field_mutability_guide`, `related_mcp_tools`. Variable JSONs set `"extends": "variable_base"` and add template-specific required attributes (e.g. value, or value + options for dom_element). `get_variable_template()` uses `load_variable_template_with_extends()`.

The same pattern is used for **triggers**: shared content lives in `tag_manager/_common/trigger_base.json`. A trigger JSON can set `"extends": "trigger_base"` and will be deep-merged at load time. `get_trigger_template()` uses `load_trigger_template_with_extends()` to resolve it.

## **🔧 MCP Tool Architecture**

### **Unified Create/Update Pattern**

```python
# Single template serves both create and update operations
get_tag_template(template_name) → {
    "mcp_usage": {
        "create_tag": { /* creation guidance */ },
        "update_tag": { /* update guidance with mutability info */ }
    },
    "required_attributes": { /* fields with mutability info */ },
    "optional_attributes": { /* fields with mutability info */ },
    "read_only_attributes": { /* API-generated fields */ },
    "field_mutability_guide": { /* comprehensive mutability documentation */ }
}
```

### **Two-Tier Discovery Pattern**

```python
# Tier 1: List available templates by component (structured responses)
get_available_tag_templates() → {
    "available_templates": ["custom_tag"],
    "total_count": 1,
    "usage_guide": {...}
}
get_available_trigger_templates() → {
    "available_templates": ["click", "page_view"],
    "total_count": 2,
    "usage_guide": {...}
}
get_available_variable_templates() → {
    "available_templates": ["constant", "custom_javascript", "dom_element", "data_layer"],
    "total_count": 4,
    "usage_guide": {...}
}

# Tier 2: Get specific template with complete create/update guidance
get_tag_template(template_name) → {comprehensive_template_with_mutability}
get_trigger_template(template_name) → {comprehensive_template_with_mutability}
get_variable_template(template_name) → {comprehensive_template_with_mutability}
```

### **MCP Tool Exposure Pattern**

```python
# In piwik_mcp/tools/tag_manager/templates.py - core functions AND MCP-exposed wrappers
def get_available_tag_templates() -> Dict[str, Any]: ...
def get_tag_template(template_name: str) -> Dict[str, Any]: ...
def get_available_trigger_templates() -> Dict[str, Any]: ...
def get_trigger_template(template_name: str) -> Dict[str, Any]: ...
def get_available_variable_templates() -> Dict[str, Any]: ...
def get_variable_template(template_name: str) -> Dict[str, Any]: ...

def register_template_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    def templates_list_tags() -> dict: ...
    @mcp.tool()
    def templates_get_tag(template_name: str) -> dict: ...
    @mcp.tool()
    def templates_list_triggers() -> dict: ...
    @mcp.tool()
    def templates_get_trigger(template_name: str) -> dict: ...
    @mcp.tool()
    def templates_list_variables() -> dict: ...
    @mcp.tool()
    def templates_get_variable(template_name: str) -> dict: ...
```

## **📄 Enhanced JSON Template Structure**

### **Standard Template Schema with Field Mutability**

```json
{
  "template_name": "custom_tag",
  "name_aliases": [
     "Human-Readable Name"
  ],
  "description": "What this template does",

  "ai_usage_guide": {
    "when_to_use": [...],
    "common_use_cases": [...]
  },

  "mcp_usage": {
    "create_tag": {
      "tool_name": "tags_create",
      "description": "Create new resource using this template",
      "required_parameters": {...},
      "optional_parameters": {...}
    },
    "update_tag": {
      "tool_name": "tags_update",
      "description": "Update existing resource - only editable fields processed",
      "required_parameters": {...},
      "optional_parameters": {...}
    }
  },

  "required_attributes": {
    "attribute_name": {
      "type": "string|boolean|integer|object",
      "mutability": "editable|create-only|read-only",
      "description": "What this does",
      "examples": [...],
      "validation": {...},
      "recommendation": "AI guidance",
      "edit_note": "⚠️ Mutability-specific notes"
    }
  },

  "optional_attributes": {
    "attribute_name": {
      "mutability": "editable|create-only",
      /* ... same structure as required */
    }
  },

  "read_only_attributes": {
    "attribute_name": {
      "mutability": "read-only",
      "description": "API-generated field",
      "edit_note": "🚫 Cannot be modified"
    }
  },

  "field_mutability_guide": {
    "description": "Understanding field editability after creation",
    "mutability_types": {
      "editable": {
        "description": "✅ Can be updated anytime",
        "examples": ["name", "priority", "is_active"]
      },
      "create-only": {
        "description": "⚠️ Set during creation, immutable after",
        "examples": ["template", "tag_type"]
      },
      "read-only": {
        "description": "🚫 Auto-generated, never user-modifiable",
        "examples": ["created_at", "updated_at"]
      }
    }
  },

  "complete_examples": {
    "create_example": {
      "description": "Creating new resource",
      "mcp_call": {
        "function": "create_tag",
        "parameters": {...}
      }
    },
    "update_example": {
      "description": "Updating existing resource",
      "mcp_call": {
        "function": "update_tag",
        "parameters": {...}
      }
    }
  },

  "common_mistakes": [...],
  "troubleshooting": {...}
}
```

## **🔄 Core Implementation Logic**

### **Template Discovery Function**

```python
def get_available_tag_templates() -> Dict[str, Any]:
    # 1. Scan assets directory for .json files
    # 2. Extract template names from filenames
    # 3. Return sorted list + usage guidance
    # 4. Handle errors gracefully
```

### **Template Details Function**

```python
def get_tag_template(template_name: str) -> Dict[str, Any]:
    # 1. Build file path from template name
    # 2. Check file exists, show available alternatives if not
    # 3. Load and parse JSON
    # 4. Return complete template documentation
    # 5. Handle JSON parsing errors
```

## **🎯 Integration Points**

### **Server Integration**

1. **Centralized registration**: all Tag Manager template tools are registered in `register_template_tools(mcp)`
2. **Server setup**: `server.py` creates the MCP server and calls `register_all_tools(mcp)` which invokes
   `register_template_tools(mcp)` (and other Tag Manager tools)
3. **Docstrings** reference discovery tools from their respective modules (e.g., in `tags_create`)

Example:

```python
from mcp.server.fastmcp import FastMCP
from piwik_mcp.tools import register_all_tools

mcp = FastMCP("Piwik PRO Analytics Server 📊")
register_all_tools(mcp)
```

### **Cross-Tool References**

```python
# In tags_create tool docstring:
"""
💡 TIP: Use these tools to discover available templates:
- templates_list_tags() - List all available templates
- templates_get_tag(template_name='custom_tag') - Get complete create/update template info
"""

# In tags_update tool docstring:
"""
💡 TIP: Use templates_get_tag(template_name='custom_tag') to see all available
fields and their mutability for any tag template.

Field Mutability:
✅ Editable: name, code, priority, consent_type, etc.
⚠️ Create-only: template, tag_type (ignored in updates)
🚫 Read-only: created_at, updated_at, is_published (filtered out automatically)
"""
```

## **📋 Replication Guide for Other Components**

### **For Triggers System**

```python
# File structure
piwik_mcp/assets/tag_manager/triggers/
├── page_view.json          # Complete create/update template
├── click.json              # Complete create/update template
├── form_submission.json    # Complete create/update template

# MCP tools with unified discovery pattern; create is implemented; update is planned
def get_available_trigger_templates() -> Dict[str, Any]
def get_trigger_template(template_name: str) -> Dict[str, Any]  # Returns mutability info

# Server exposure (via register_template_tools)
templates_list_triggers()
templates_get_trigger(template_name: str)  # Includes mcp_usage.update_trigger in template docs

# Template JSON structure includes:
{
  "mcp_usage": {
    "create_trigger": {...},
    "update_trigger": {...}  # With field mutability guidance (wrapper not exposed yet)
  },
  "required_attributes": {
    "name": {"mutability": "editable", ...},
    "trigger_type": {"mutability": "create-only", ...}
  },
  "field_mutability_guide": {...}
}
```

### **For Variables System**

```python
# File structure
piwik_mcp/assets/tag_manager/variables/
├── constant.json           # Complete create/update template
├── custom_javascript.json  # Complete create/update template
├── dom_element.json        # Complete create/update template
├── data_layer.json         # Complete create/update template

# MCP tools with unified create/update pattern (both exposed)
def get_available_variable_templates() -> Dict[str, Any]
def get_variable_template(template_name: str) -> Dict[str, Any]  # Returns mutability info

# Server exposure (via register_template_tools)
templates_list_variables()
templates_get_variable(template_name: str)  # Includes mcp_usage.update_variable

# Template JSON structure includes:
{
  "mcp_usage": {
    "create_variable": {...},
    "update_variable": {...}  # With field mutability guidance
  },
  "required_attributes": {
    "name": {"mutability": "editable", ...},
    "template": {"mutability": "create-only", ...}
  },
  "field_mutability_guide": {...}
}
```

## **✨ Key Success Principles**

### **1. Consistency**

- Same file naming pattern across all components
- Same JSON structure with mutability fields
- Same MCP tool naming (prefix + component + action)
- Same error handling approach
- **Unified create/update pattern** - one template for both operations

### **2. Field Mutability Awareness**

- **Clear mutability classification**: editable, create-only, read-only
- **Visual indicators**: ✅ ⚠️ 🚫 for immediate recognition
- **Automatic filtering**: API layer respects mutability constraints
- **Update guidance**: Clear examples of what can/cannot be changed

### **3. AI Optimization**

- **Complete examples** with real MCP function calls for both create and update
- **Clear attribute explanations** with mutability and validation rules
- **Troubleshooting guides** with create vs update specific instructions
- **Strategic emoji usage** for mutability status and priority signals
- **Cross-operation guidance** - templates explain both creation and editing

### **4. Maintainability**

- **Single source of truth** - one template file per resource type
- **No duplicate templates** - same file serves create and update
- **Self-documenting** - template name = filename, mutability = explicit
- **Independent files** - easy to add/modify individual templates
- **Validation built-in** - JSON parsing catches syntax errors

### **5. Discoverability**

- **Two-tier discovery** (list → details) with operation-specific guidance
- **Usage guidance** for both create and update in every response
- **Cross-references** between related tools and operations
- **Workflow examples** showing complete create → update → manage processes
- **Field exploration** - easy to discover what's editable vs immutable

## **🔄 Implementation Steps for New Component**

### **Phase 1: Setup**

1. **Create directory structure** (`assets/tag_manager/{component}/`)
2. **Implement core functions** (get_available_X_templates, get_X_template)
3. **Ensure** `register_template_tools(mcp)` is included in tool registration via `register_all_tools(mcp)`

### **Phase 2: Template Creation**

4. **Create first template JSON** with complete create/update documentation including:
   - `mcp_usage` section with both create and update operations
   - `mutability` field on all attributes (editable/create-only/read-only)
   - `field_mutability_guide` section
   - Examples for both create and update scenarios
5. **Add API client mutability support** (field filtering in update operations)
6. **Update related tool docstrings** with discovery references and mutability info

### **Phase 3: Validation & Integration**

7. **Test JSON validation** and error handling for both operations
8. **Test field mutability filtering** in API calls
9. **Add imports** and server registration
10. **Create comprehensive examples** showing create → update workflows

### **Field Mutability Implementation Pattern**

```python
# Tags (API client enforces filtering)
editable_only = attributes.model_dump(
    by_alias=True,
    exclude_none=True,
    exclude={
        'createdAt', 'created_at', 'updatedAt', 'updated_at', 'is_published',
        'template', 'tag_type'
    }
)

# Variables (tool layer enforces filtering via update model; API passes only allowed fields)
# VariableUpdateAttributes does not include create-only/read-only fields like variable_type/created_at/updated_at.
# The tool constructs kwargs from this model, so update requests contain only editable fields.

# Triggers
# Template JSON documents mutability, but a dedicated update tool wrapper is not exposed yet.
# If updating through the API client, avoid sending create-only fields like trigger_type.
```

This enhanced architecture provides **scalable, maintainable, AI-friendly documentation with complete create/update lifecycle support** that can be replicated across all Tag Manager components! 🚀

### **🎯 Next Implementation Targets**

1. **Cross-component workflows**: Templates that reference multiple component types
2. **Advanced examples**: Complex scenarios showing component interactions
