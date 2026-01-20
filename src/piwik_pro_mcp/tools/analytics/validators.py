"""
Validation models for custom dimensions attributes.

These models validate scope-specific attributes passed to custom dimensions tools.
They provide type safety and clear error messages at runtime.
"""

import re
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, model_validator


class ExtractionConfigDict(BaseModel):
    """
    Extraction configuration for custom dimensions.

    Extraction rules automatically populate dimension values from page data:

    QUERY PARAMETER TARGET:
      • target: "page_query_parameter"
      • pattern: Exact query parameter name (e.g., "utm_campaign")
      • Extracts: ?utm_campaign=spring_sale → "spring_sale"

    REGEX TARGETS:
      • target: "page_title_regex" or "page_url_regex"
      • pattern: Regex with AT LEAST ONE capture group ()
      • Extracts: The first capture group becomes the dimension value

      Examples:
        ✓ "/products/(.*?)/"      → URL /products/shoes/ → "shoes"
        ✓ "/category/([^/]+)"     → URL /category/electronics → "electronics"
        ✓ "^(.*?) \\|"            → Title "Blog Post | Site" → "Blog Post"
        ✗ ".*/something.*"        → NO CAPTURE GROUP (invalid!)
        ✗ "/something"            → NO CAPTURE GROUP (invalid!)

    IMPORTANT: For regex targets, patterns WITHOUT capture groups will be rejected!
    """

    target: Literal["page_title_regex", "page_url_regex", "page_query_parameter"] = Field(
        ...,
        description="What value should be extracted from page data",
    )
    pattern: str = Field(
        ...,
        description="Regex pattern with capture group () or exact query parameter name",
        examples=[
            "utm_campaign",  # Query parameter
            "/products/(.*?)/",  # Regex with capture group
            "/category/([^/]+)",  # Another valid regex
        ],
    )

    @model_validator(mode="after")
    def validate_pattern_for_regex_targets(self) -> "ExtractionConfigDict":
        """Validate pattern based on target type."""
        # For regex targets, pattern should have capture groups
        if self.target in ("page_title_regex", "page_url_regex"):
            try:
                compiled = re.compile(self.pattern)
                if compiled.groups == 0:
                    raise ValueError(
                        f"Regex pattern must contain at least one capture group ().\n"
                        f"\n"
                        f"Examples of VALID patterns:\n"
                        f'  ✓ "/products/(.*?)/"      - captures product name\n'
                        f'  ✓ "/category/([^/]+)"     - captures category\n'
                        f'  ✓ "/(.*)/something"       - captures first path segment\n'
                        f"\n"
                        f"Your pattern:\n"
                        f'  ✗ "{self.pattern}"  - NO CAPTURE GROUP\n'
                        f"\n"
                        f"💡 Tip: Add parentheses () around the part you want to capture."
                    )
            except re.error as e:
                raise ValueError(f"Invalid regex syntax in pattern.\nPattern: {self.pattern}\nError: {e}")

        return self

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"target": "page_query_parameter", "pattern": "utm_campaign"},
                {"target": "page_url_regex", "pattern": "/products/(.*?)/"},
                {"target": "page_title_regex", "pattern": "^(.*?) \\|"},
            ]
        }
    }


class StandardDimensionAttrs(BaseModel):
    """
    Validation model for standard (session/event) custom dimension attributes.

    Used to validate attributes dict for session and event-scoped dimensions.
    """

    active: bool = Field(
        ...,
        description="Whether dimension is active and collecting data",
    )
    case_sensitive: bool = Field(
        ...,
        description="Whether dimension values are case-sensitive (e.g., 'User' vs 'user')",
    )
    slot: Optional[int] = Field(
        None,
        ge=1,
        description="Slot number. Optional - auto-assigned by API if not provided. Cannot be changed after creation.",
    )
    extractions: Optional[List[ExtractionConfigDict]] = Field(
        None,
        description="Value extraction rules to automatically populate dimension from page data",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                # Minimal example
                {"active": True, "case_sensitive": False},
                # With slot
                {"active": True, "case_sensitive": False, "slot": 5},
                # With extraction
                {
                    "active": True,
                    "case_sensitive": False,
                    "extractions": [{"target": "page_query_parameter", "pattern": "utm_campaign"}],
                },
                # Full example
                {
                    "active": True,
                    "case_sensitive": False,
                    "slot": 3,
                    "extractions": [
                        {"target": "page_query_parameter", "pattern": "utm_source"},
                        {"target": "page_url_regex", "pattern": "/category/(.*?)/"},
                    ],
                },
            ]
        }
    }


class StandardDimensionUpdateAttrs(BaseModel):
    """
    Validation model for standard dimension update attributes.

    Note: slot is NOT included as it's readonly and cannot be updated.
    """

    active: bool = Field(
        ...,
        description="Whether dimension is active and collecting data",
    )
    case_sensitive: bool = Field(
        ...,
        description="Whether dimension values are case-sensitive",
    )
    extractions: Optional[List[ExtractionConfigDict]] = Field(
        None,
        description="Updated value extraction rules",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                # Minimal update
                {"active": False, "case_sensitive": True},
                # With extractions
                {
                    "active": True,
                    "case_sensitive": False,
                    "extractions": [{"target": "page_query_parameter", "pattern": "utm_medium"}],
                },
                # Clear extractions
                {"active": True, "case_sensitive": False, "extractions": []},
            ]
        }
    }


class ProductDimensionAttrs(BaseModel):
    """
    Validation model for product custom dimension attributes (CREATE operation).

    Used for creating product dimensions.
    """

    slot: int = Field(
        ...,
        ge=1,
        description="Slot number. REQUIRED for product dimensions. Cannot be changed later.",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"slot": 1},
                {"slot": 5},
            ]
        }
    }


class ProductDimensionUpdateAttrs(BaseModel):
    """
    Validation model for product custom dimension UPDATE attributes.

    Product dimensions do NOT support attribute updates. Only name and description
    can be updated (via main parameters, not attributes).

    The slot number CANNOT be changed after creation. If you need a different slot,
    you must delete and recreate the dimension.

    Attributes should be an empty dict: {}
    """

    model_config = {
        "extra": "forbid",  # Reject any attributes passed
        "json_schema_extra": {
            "examples": [
                {},  # Empty dict - no attributes supported for product updates
            ]
        },
    }
