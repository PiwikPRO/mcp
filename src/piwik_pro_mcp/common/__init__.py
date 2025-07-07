"""
Common utilities and shared components for Piwik PRO MCP tools.

This module provides shared functionality used across all MCP tool modules,
including client creation, validation, parameter discovery, and template utilities.
"""

from .telemetry import mcp_telemetry_wrapper
from .utils import create_piwik_client, validate_data_against_model

__all__ = [
    # Client and validation utilities
    "create_piwik_client",
    "validate_data_against_model",
    # Telemetry
    "mcp_telemetry_wrapper",
]
