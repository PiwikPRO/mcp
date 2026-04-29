"""
Template loading and discovery utilities.

This module provides utilities for loading JSON schema templates
and discovering available templates in the assets directory.
Tag templates may use "extends": "base_name" to inherit from a shared
JSON under assets/tag_manager/_common/; the loader deep-merges base
with the template (template keys win).
"""

import json
from pathlib import Path
from typing import Any


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge overlay into base. For dicts, overlay wins on conflict; for lists/other, overlay replaces."""
    result = dict(base)
    for key, overlay_val in overlay.items():
        if key not in result:
            result[key] = overlay_val
        elif isinstance(overlay_val, dict) and isinstance(result[key], dict):
            result[key] = _deep_merge(result[key], overlay_val)
        else:
            result[key] = overlay_val
    return result


def get_tag_manager_common_path() -> Path:
    """Path to tag_manager _common directory (shared base JSONs)."""
    return get_assets_base_path() / "tag_manager" / "_common"


def _load_base_with_extends(base_path: Path, common_dir: Path) -> dict[str, Any]:
    """
    Load a base JSON and recursively resolve its "extends" chain.
    Returns the fully resolved base (extends key removed from result).
    """
    with open(base_path, encoding="utf-8") as f:
        base = json.load(f)
    extends = base.pop("extends", None)
    if not extends:
        return base
    parent_path = common_dir / f"{extends}.json"
    if not parent_path.exists():
        raise RuntimeError(f"Extended base not found: {parent_path}")
    parent = _load_base_with_extends(parent_path, common_dir)
    return _deep_merge(parent, base)


def _load_template_with_extends(asset_path: Path, common_dir: Path) -> dict[str, Any]:
    """
    Load a template JSON and resolve "extends" by deep-merging with a base from common_dir.

    If the template has "extends": "base_name", loads common_dir/base_name.json
    (recursively resolving any chain of extends) and merges with the template (template wins).
    The "extends" key is removed from the result.
    """
    with open(asset_path, encoding="utf-8") as f:
        data = json.load(f)
    extends = data.pop("extends", None)
    if not extends:
        return data
    base_path = common_dir / f"{extends}.json"
    if not base_path.exists():
        raise RuntimeError(f"Extended base not found: {base_path}")
    base = _load_base_with_extends(base_path, common_dir)
    return _deep_merge(base, data)


def load_tag_template_with_extends(asset_path: Path) -> dict[str, Any]:
    """Load a tag template JSON and resolve \"extends\" from tag_manager/_common."""
    return _load_template_with_extends(asset_path, get_tag_manager_common_path())


def load_trigger_template_with_extends(asset_path: Path) -> dict[str, Any]:
    """Load a trigger template JSON and resolve \"extends\" from tag_manager/_common."""
    return _load_template_with_extends(asset_path, get_tag_manager_common_path())


def load_variable_template_with_extends(asset_path: Path) -> dict[str, Any]:
    """Load a variable template JSON and resolve \"extends\" from tag_manager/_common."""
    return _load_template_with_extends(asset_path, get_tag_manager_common_path())


def get_assets_base_path() -> Path:
    """Get the base path for MCP template assets."""
    current_dir = Path(__file__).parent.parent
    assets_path = current_dir / "assets"

    if not assets_path.exists():
        raise RuntimeError(f"Assets directory not found at: {assets_path}")

    return assets_path


def load_template_asset(asset_path: Path) -> dict[str, Any]:
    """Load and parse a template asset JSON file."""
    try:
        with open(asset_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load template asset {asset_path}: {str(e)}")


def list_available_assets(directory: Path | str) -> dict[str, dict[str, Any]]:
    """Return metadata for available template assets keyed by template name.

    Args:
        directory: Either a full directory path or a relative path under the assets base directory
                   (e.g., "tag_manager/tags").

    Returns:
        Mapping in shape:
        {
            "template_name": {
                "name_aliases": [...],
                "description": "..."
            }
        }
    """
    path = Path(directory)

    if not path.is_absolute():
        path = get_assets_base_path() / path

    if not path.exists():
        raise RuntimeError("Templates directory not found. No templates are currently available.")

    templates = sorted(path.glob("*.json"), key=lambda p: p.stem)

    if not templates:
        raise RuntimeError("No templates found in templates directory.")

    assets: dict[str, dict[str, Any]] = {}
    for template_path in templates:
        template_name = template_path.stem
        template_data = load_template_asset(template_path)
        name_aliases = template_data.get("name_aliases")

        assets[template_name] = {
            "name_aliases": name_aliases if isinstance(name_aliases, list) else [],
            "description": template_data.get("description", ""),
        }

    return assets
