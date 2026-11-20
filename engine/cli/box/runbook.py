"""`box runbook`: render runbooks/*.md with values from company.yaml."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .repo import BoxError, load_company, load_yaml

PLACEHOLDER_RE = re.compile(r"\{([a-z_][a-z0-9_.]*)\}")
RENDERED_DIR = "runbooks/rendered"


def _flatten(value: Any, prefix: str, out: dict[str, list[tuple[str, Any]]]) -> None:
    if isinstance(value, dict):
        for k, v in value.items():
            path = f"{prefix}.{k}" if prefix else str(k)
            out.setdefault(path, []).append((path, v))
            out.setdefault(str(k), []).append((path, v))
            _flatten(v, path, out)


def context(root: Path) -> dict[str, list[tuple[str, Any]]]:
    """Every value reachable by full dotted path or by its last key."""
    company = load_company(root)
    out: dict[str, list[tuple[str, Any]]] = {}
    _flatten(company, "", out)
    retention_rel = (company.get("files") or {}).get("retention")
    if retention_rel and (root / retention_rel).is_file():
        retention = load_yaml(root / retention_rel) or {}
        for k, v in retention.items():
            if not isinstance(v, (dict, list)):
                out.setdefault(str(k), []).append((f"{retention_rel} > {k}", v))
    return out


def _format(path: str, value: Any) -> str:
    if value in ("", None, []):
        return f"(not set: {path})"
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return str(value)


def render_text(text: str, ctx: dict[str, list[tuple[str, Any]]], source: str) -> tuple[str, list[str]]:
    errors: list[str] = []

    def sub(m: re.Match[str]) -> str:
        key = m.group(1)
        matches = ctx.get(key, [])
        distinct = {p for p, _ in matches}
        if not matches:
            errors.append(f"{source}: unknown placeholder {{{key}}}")
            return m.group(0)
        if len(distinct) > 1:
            errors.append(f"{source}: placeholder {{{key}}} is ambiguous: {', '.join(sorted(distinct))}")
            return m.group(0)
        path, value = matches[0]
        return _format(path, value)

    return PLACEHOLDER_RE.sub(sub, text), errors


def render_all(root: Path) -> tuple[list[Path], list[str]]:
    ctx = context(root)
    src_dir = root / "runbooks"
    out_dir = root / RENDERED_DIR
    written: list[Path] = []
    errors: list[str] = []
    sources = sorted(src_dir.glob("*.md"))
    if not sources:
        raise BoxError("no runbooks/*.md to render")
    env = (load_company(root).get("workspace") or {}).get("environment", "")
    out_dir.mkdir(parents=True, exist_ok=True)
    for src in sources:
        text, errs = render_text(src.read_text(encoding="utf-8"), ctx, str(src.relative_to(root)))
        errors.extend(errs)
        header = f"<!-- Rendered by `box runbook` from runbooks/{src.name} for environment `{env}`. Do not edit. -->\n\n"
        dest = out_dir / src.name
        dest.write_text(header + text, encoding="utf-8")
        written.append(dest)
    return written, errors
