"""
Centralized accessors for environment-driven configuration flags.

This module provides typed helper functions for reading environment variables
used across the project, keeping parsing logic and defaults in one place.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

_TRUTHY_VALUES = {"1", "true", "yes", "on"}
_FALSY_VALUES = {"0", "false", "no", "off"}


def _get_env(name: str) -> Optional[str]:
    """Return environment variable value or None when unset."""

    return os.getenv(name)


def _get_bool(name: str, *, default: bool) -> bool:
    """Parse boolean environment variable with shared semantics."""

    value = _get_env(name)
    if value is None:
        return default

    normalized = value.strip().lower()
    if not normalized:
        return default

    if normalized in _TRUTHY_VALUES:
        return True

    if normalized in _FALSY_VALUES:
        return False

    return default


@lru_cache(maxsize=None)
def telemetry_enabled() -> bool:
    """Return whether telemetry should be enabled."""

    return _get_bool("PIWIK_PRO_TELEMETRY", default=True)


@lru_cache(maxsize=None)
def tag_manager_resource_check_enabled() -> bool:
    """Return whether Tag Manager resource validation should run."""

    return _get_bool("PIWIK_PRO_TM_RESOURCE_CHECK", default=True)


@lru_cache(maxsize=None)
def safe_mode_enabled() -> bool:
    """Return whether safe mode (read-only) is enabled.

    When enabled, only read-only tools are exposed through the MCP server.
    Write operations (create, update, delete, publish) are not available.

    Safe mode is enabled by default to let users safely explore their data.
    Set PIWIK_PRO_SAFE_MODE=0 to enable write operations.
    """

    return _get_bool("PIWIK_PRO_SAFE_MODE", default=True)
