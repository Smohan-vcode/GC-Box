"""Locating the repository and loading its YAML files."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

COMPANY_FILE = "company.yaml"
SCHEMA_FILE = "schema/company.schema.json"


class BoxError(Exception):
    """An error reported to the user without a traceback."""


def find_root(start: Path | None = None) -> Path:
    """Return the repository root: $BOX_ROOT, or the nearest parent holding company.yaml."""
    env = os.environ.get("BOX_ROOT")
    if env:
        root = Path(env).resolve()
        if not (root / COMPANY_FILE).is_file():
            raise BoxError(f"BOX_ROOT={env} has no {COMPANY_FILE}")
        return root
    here = (start or Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        if (candidate / COMPANY_FILE).is_file():
            return candidate
    raise BoxError(f"no {COMPANY_FILE} found in {here} or any parent; set BOX_ROOT")


def load_yaml(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as fh:
            return yaml.safe_load(fh)
    except FileNotFoundError:
        raise BoxError(f"{path} not found") from None
    except yaml.YAMLError as exc:
        raise BoxError(f"{path}: invalid YAML: {exc}") from None


def load_company(root: Path) -> dict[str, Any]:
    data = load_yaml(root / COMPANY_FILE)
    if not isinstance(data, dict):
        raise BoxError(f"{COMPANY_FILE} must be a mapping")
    return data
