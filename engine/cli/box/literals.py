"""`box check-literals`: rule R1, no company-specific value outside the data paths."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .repo import load_company, load_yaml

CHECKED_DIRS = ("engine", "defaults", "tasks", "spikes", "assistants", "docs")
SKIP_PARTS = {".terraform", "__pycache__", "node_modules", ".venv"}
EXEMPT_MARKER = "example:"
MIN_LENGTH = 3


@dataclass
class Hit:
    path: Path
    line: int
    literal: str
    text: str


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [s for v in value for s in _strings(v)]
    if isinstance(value, dict):
        return [s for v in value.values() for s in _strings(v)]
    return []


def collect_literals(root: Path) -> list[str]:
    """Company values (company.yaml > company, test domain, DNS zone) and people's full names."""
    company = load_company(root)
    found = _strings(company.get("company", {}))
    found.append((company.get("workspace") or {}).get("test_domain", ""))
    found.append((company.get("dns") or {}).get("zone", ""))
    users_rel = (company.get("files") or {}).get("users", "directory/users.yaml")
    users = (load_yaml(root / users_rel) or {}).get("users") or []
    for u in users:
        full = " ".join(p for p in (u.get("given_name"), u.get("family_name")) if p)
        if u.get("given_name") and u.get("family_name"):
            found.append(full)
    uniq = {s.strip() for s in found if s and len(s.strip()) >= MIN_LENGTH}
    # Longest first so a report names the most specific value.
    return sorted(uniq, key=lambda s: (-len(s), s))


def check_literals(root: Path, dirs: tuple[str, ...] = CHECKED_DIRS) -> list[Hit]:
    literals = [(lit, lit.lower()) for lit in collect_literals(root)]
    hits: list[Hit] = []
    for d in dirs:
        base = root / d
        if not base.is_dir():
            continue
        for path in sorted(p for p in base.rglob("*") if p.is_file()):
            if SKIP_PARTS & set(path.relative_to(root).parts):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for lineno, line in enumerate(text.splitlines(), 1):
                if EXEMPT_MARKER in line:
                    continue
                low = line.lower()
                for lit, lit_low in literals:
                    if lit_low in low:
                        hits.append(Hit(path.relative_to(root), lineno, lit, line.strip()))
                        break
    return hits
