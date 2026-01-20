"""
Common utilities for Piwik PRO MCP tools.

This module provides shared utility functions used across all MCP tool modules,
including client creation and data validation.
"""

import os
from typing import Any, Dict, Optional, Type

import requests
from pydantic import BaseModel, ValidationError

from piwik_pro_mcp.api.client import PiwikProClient


def fetch_json_from_url(url: str, timeout: int = 5) -> dict | list:
    """
    Fetch JSON from an unauthenticated URL.

    This is a simple utility for fetching public JSON resources (e.g., enum definitions).
    """
    headers = {"Accept": "application/json"}

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.Timeout:
        raise RuntimeError(f"Timeout fetching JSON from {url}")
    except requests.HTTPError as e:
        raise RuntimeError(f"HTTP error fetching JSON from {url}: {e.response.status_code}")
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch JSON from {url}: {str(e)}")
    except ValueError:
        raise RuntimeError(f"Invalid JSON response from {url}")


def create_piwik_client() -> PiwikProClient:
    """Create an authenticated Piwik PRO client using client credentials."""
    # Get Piwik PRO host from environment
    piwik_host = os.getenv("PIWIK_PRO_HOST")
    if not piwik_host:
        raise RuntimeError("PIWIK_PRO_HOST environment variable not configured.")

    # Get client credentials from environment
    client_id = os.getenv("PIWIK_PRO_CLIENT_ID")
    client_secret = os.getenv("PIWIK_PRO_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise RuntimeError(
            "Client credentials not configured. "
            "Set PIWIK_PRO_CLIENT_ID and PIWIK_PRO_CLIENT_SECRET environment variables."
        )

    try:
        return PiwikProClient(client_id=client_id, client_secret=client_secret, host=piwik_host)
    except Exception as e:
        raise RuntimeError(f"Failed to create Piwik PRO client: {str(e)}")


def validate_data_against_model(
    data: Optional[Dict[str, Any]],
    model_class: Type[BaseModel],
    invalid_item_label: str = "attribute",
) -> Optional[BaseModel]:
    """
    Validate a dictionary against a Pydantic model with configurable behavior.

    Args:
        data: Optional dictionary to validate
        model_class: Pydantic model class to validate against
        allow_none: If True, returns None when data is None instead of raising
        aggregate_errors: If True, formats errors as a list of concise messages
        invalid_item_label: Label used in aggregated error messages (e.g., "filter")

    Returns:
        Validated model instance or None (when allow_none is True and data is None)

    Raises:
        RuntimeError: If validation fails
    """
    if data is None:
        raise RuntimeError("Validation error: no data provided")
    try:
        return model_class(**data)
    except ValidationError as e:
        error_messages = []
        for error in e.errors():
            message = f"Invalid {invalid_item_label}: {error.get('loc')}. {error.get('msg')}"
            error_messages.append(message)
        raise RuntimeError(f"{error_messages}")
