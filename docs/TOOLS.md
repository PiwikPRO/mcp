# Available Tools

This document provides a complete reference of all MCP tools available in the Piwik PRO MCP Server.

## Parameter Discovery

- `tools_parameters_get(tool_name)` - Get JSON schema for any tool's parameters

## App Management

- `apps_list(limit, offset, search)` - List all apps with filtering and pagination
- `apps_get(app_id)` - Get detailed information about a specific app
- `apps_create(attributes)` - Create a new app using JSON attributes
- `apps_update(app_id, attributes)` - Update existing app using JSON attributes
- `apps_delete(app_id)` - Delete an app (irreversible)

## Analytics

### Annotations

- `analytics_annotations_list(app_id, date_from, date_to, source, limit, offset)` - List annotations for an app; supports user and system annotations. Use `source` to filter: "all", "user", or "system".
- `analytics_annotations_get(annotation_id, app_id)` - Get a specific user annotation by ID
- `analytics_annotations_create(app_id, content, date, visibility)` - Create a user annotation (default visibility is "private")
- `analytics_annotations_update(annotation_id, app_id, content, date, visibility)` - Update an existing user annotation (default visibility is "private")
- `analytics_annotations_delete(annotation_id, app_id)` - Delete a user annotation by ID

### Goals

- `analytics_goals_list(website_id, limit, offset)` - List all goals for a website with pagination
- `analytics_goals_get(goal_id, website_id)` - Get detailed information about a specific goal
- `analytics_goals_create(website_id, name, trigger, revenue, description?, pattern_type?, pattern?, allow_multiple?, case_sensitive?)` - Create a new goal. Supports triggers: url, title, event_name, event_category, event_action, file, external_website, manually. For non-manual triggers, pattern_type and pattern are required.
- `analytics_goals_update(goal_id, website_id, name, trigger, revenue, description?, pattern_type?, pattern?, allow_multiple?, case_sensitive?)` - Update an existing goal. Required fields: name, trigger, revenue, website_id. For non-manual triggers, pattern_type and pattern are required.
- `analytics_goals_delete(goal_id, website_id)` - Delete a goal (irreversible)

### Custom Dimensions

- `analytics_custom_dimensions_list(website_id, scope?, limit, offset)` - List custom dimensions with optional scope filter. When scope is None, returns both standard and product dimensions separately. Supports filtering by "session", "event", or "product".
- `analytics_custom_dimensions_get(dimension_id, website_id, scope)` - Get a specific custom dimension by ID. Scope parameter ("session", "event", or "product") is required for API routing.
- `analytics_custom_dimensions_create(website_id, name, scope, description?, slot?, active?, case_sensitive?, extractions?)` - Create a custom dimension with specified scope
- `analytics_custom_dimensions_update(dimension_id, website_id, name, scope, description?, slot?, active?, case_sensitive?, extractions?)` - Update an existing custom dimension
- `analytics_custom_dimensions_get_slots(website_id)` - Get slot availability statistics for all dimension types (session, event, and product). Returns available, used, and remaining slots for each scope.

### Query API

- `analytics_query_execute(website_id, columns, date_from, date_to, filters?, offset?, limit?, metric_filters?, order_by?, order_direction?)` - Execute analytics queries with metrics, dimensions, filters, and flexible date ranges. Supports both absolute dates (YYYY-MM-DD) and relative dates (today, yesterday, last_7_days, etc.)
- `analytics_dimensions_list(website_id)` - List all available dimensions for a website, excluding deprecated dimensions
- `analytics_metrics_list(website_id)` - List all available metrics for a website, separating standard metrics from calculated metrics
- `analytics_dimensions_details_list(website_id, dimensions)` - Get detailed information about specific dimensions including data types, available transformations, and enum values where applicable
- `analytics_metrics_details_list(website_id, metrics)` - Get detailed information about specific metrics including data types and available transformations

## Container Settings

- `container_settings_get_installation_code(app_id)` - Get installation code snippet for embedding the container
- `container_settings_list(app_id)` - Get app container settings (JSON:API list with pagination)

## Tag Manager

### Tags

- `tags_list(app_id, limit, offset, filters)` - List tags
- `tags_get(app_id, tag_id)` - Get specific tag details
- `tags_create(app_id, attributes)` - Create new tag using JSON attributes
- `tags_update(app_id, tag_id, attributes)` - Update existing tag using JSON attributes
- `tags_delete(app_id, tag_id)` - Delete tag (irreversible)
- `tags_copy(app_id, tag_id, target_app_id?, name?, with_triggers=false)` - Copy a tag within the same app or to another app. Supports optional rename and copying attached triggers (set `with_triggers=true`).

### Relationships

- `tags_list_triggers(app_id, tag_id, limit, offset, sort, name, trigger_type)` - List triggers attached to a tag
- `triggers_list_tags(app_id, trigger_id, limit, offset, sort, name, is_active, template, consent_type, is_prioritized)` - List tags assigned to a trigger

### Triggers

- `triggers_list(app_id, limit, offset, filters)` - List triggers
- `triggers_get(app_id, trigger_id)` - Get specific trigger details
- `triggers_create(app_id, attributes)` - Create new trigger using JSON attributes
- `triggers_copy(app_id, trigger_id, target_app_id?, name?)` - Copy a trigger within the same app to another app. Supports optional rename.

### Variables

- `variables_list(app_id, limit, offset, filters)` - List variables
- `variables_get(app_id, variable_id)` - Get specific variable details
- `variables_create(app_id, attributes)` - Create new variable using JSON attributes
- `variables_update(app_id, variable_id, attributes)` - Update an existing variable using JSON attributes
- `variables_copy(app_id, variable_id, target_app_id?, name?)` - Copy a variable within the same app or to another app. Supports optional rename.

### Supported Templates

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

### Template Discovery

- `templates_list()` - List available tag templates
- `templates_get_tag(template_name)` - Get detailed documentation for a tag template
- `templates_list_triggers()` - List available trigger templates
- `templates_get_trigger(template_name)` - Get detailed documentation for a trigger template
- `templates_list_variables()` - List available variable templates
- `templates_get_variable(template_name)` - Get detailed documentation for a variable template

> **Note**: Additional templates for Google Analytics, Piwik PRO, e-commerce tracking, and other platforms are planned for future implementation. The current templates provide a solid foundation for custom tracking implementations.

### Versions

- `versions_list(app_id, limit, offset)` - List all versions
- `versions_get_draft(app_id)` - Get current draft version
- `versions_get_published(app_id)` - Get published/live version
- `versions_publish_draft(app_id)` - Publish draft to make it live

## Customer Data Platform (CDP)

- `audiences_list(app_id)` - List all audiences for an app
- `audiences_get(app_id, audience_id)` - Get detailed audience information
- `audiences_create(app_id, attributes)` - Create new audience using JSON attributes
- `audiences_update(app_id, audience_id, attributes)` - Update existing audience using JSON attributes
- `audiences_delete(app_id, audience_id)` - Delete an audience (irreversible)
- `activations_attributes_list(app_id)` - List all available CDP attributes for audience creation

## Tracker Settings

- `tracker_settings_global_get()` - Get global tracker settings
- `tracker_settings_global_update(attributes)` - Update global tracker settings using JSON attributes
- `tracker_settings_app_get(app_id)` - Get app-specific tracker settings
- `tracker_settings_app_update(app_id, attributes)` - Update app tracker settings using JSON attributes
- `tracker_settings_app_delete(app_id, setting)` - Delete specific tracker setting
