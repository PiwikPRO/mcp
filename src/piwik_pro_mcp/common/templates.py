"""
Template loading and discovery utilities.

This module provides utilities for loading JSON schema templates
and discovering available templates in the assets directory.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Union


def get_assets_base_path() -> Path:
    """Get the base path for MCP template assets."""
    current_dir = Path(__file__).parent.parent
    assets_path = current_dir / "assets"

    if not assets_path.exists():
        raise RuntimeError(f"Assets directory not found at: {assets_path}")

    return assets_path


def load_template_asset(asset_path: Path) -> Dict[str, Any]:
    """Load and parse a template asset JSON file."""
    try:
        with open(asset_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load template asset {asset_path}: {str(e)}")


def list_template_names(directory: Union[Path, str]) -> List[str]:
    """Return sorted template names (without extension) from a directory.

    Args:
        directory: Either a full directory path or a relative path under the assets base directory
                   (e.g., "tag_manager/tags").

    Returns:
        Sorted list of template base names without the `.json` suffix.
        Returns an empty list if the directory does not exist or contains no JSON files.
    """
    path = Path(directory)

    if not path.is_absolute():
        path = get_assets_base_path() / path

    if not path.exists():
        raise RuntimeError("Templates directory not found. No templates are currently available.")

    templates = sorted([p.stem for p in path.glob("*.json")])

    if not templates:
        raise RuntimeError("No templates found in templates directory.")

    return templates
