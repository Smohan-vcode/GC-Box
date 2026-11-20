"""`box validate`: schema, referenced files, cross-references and required values."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jsonschema

from .repo import COMPANY_FILE, SCHEMA_FILE, BoxError, load_company, load_yaml
from .tasks import Task, ancestors, load_tasks

# `key: ""   # REQUIRED before T9-02` -> qualifier "before T9-02"
_REQ_RE = re.compile(r"#\s*REQUIRED\b:?\s*(?P<qual>[^#]*)")
_GATE_RE = re.compile(r"\bbefore\s+(?P<gate>T\d+(?:-\d+)?|S-\d+)\b")
_KEY_RE = re.compile(r"^(?P<indent>\s*)(?P<dash>-\s+)?(?P<key>[^\s#:][^:#]*?)\s*:(?:\s+(?P<value>.*))?$")


@dataclass
class Required:
    """A value marked `# REQUIRED` in a YAML file."""

    file: str
    path: str  # dotted, list items as users[founder]
    empty: bool
    gate: str | None  # task or track id, e.g. T1 or T9-02
    note: str  # free-text qualifier, e.g. "before any template is sendable"
    line: int


def _strip_value(raw: str | None) -> str:
    if raw is None:
        return ""
    value = raw.split(" #", 1)[0].strip()
    if value.startswith("#"):
        value = ""
    return value


def _is_empty(value: str) -> bool:
    return value in ("", '""', "''", "[]", "~", "null")


def scan_required(root: Path, rel: str) -> list[Required]:
    """Find `# REQUIRED` markers in a YAML file, with dotted paths.

    Handles the block style used in this repository: nested mappings and
    lists of mappings whose items are named by `id` or `name`.
    """
    path = root / rel
    if not path.is_file():
        return []
    stack: list[tuple[int, str]] = []  # (indent of the line that opened the block, path)
    out: list[Required] = []
    last_qual: dict[str, tuple[str | None, str]] = {}
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = _KEY_RE.match(line)
        if not m:
            continue
        indent = len(m.group("indent"))
        key = m.group("key").strip().strip("\"'")
        raw = m.group("value")
        value = _strip_value(raw)
        while stack and stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1] if stack else ""
        if m.group("dash"):
            # `- id: founder` opens list element `users[founder]`.
            name = value.strip("\"'") if key in ("id", "name") else str(lineno)
            parent = f"{parent}[{name}]"
            stack.append((indent, parent))
            indent += len(m.group("dash"))
        full = f"{parent}.{key}" if parent else key
        if value == "":
            stack.append((indent, full))  # opens a nested block
        req = _REQ_RE.search(line)
        if req:
            qual = req.group("qual").strip()
            gm = _GATE_RE.search(qual)
            gate = gm.group("gate") if gm else None
            # "before <event>" scopes the marker; any other text just describes the value.
            note = qual if (qual.startswith("before") and not gate) else ""
            if not qual.startswith("before"):  # a bare marker inherits the previous qualifier in the same block
                gate, note = last_qual.get(parent, (None, ""))
            else:
                last_qual[parent] = (gate, note)
            out.append(Required(rel, full, _is_empty(value), gate, note, lineno))
    return out


def all_required(root: Path, company: dict[str, Any]) -> list[Required]:
    files = [COMPANY_FILE, *sorted(set((company.get("files") or {}).values()))]
    out: list[Required] = []
    for rel in files:
        out.extend(scan_required(root, rel))
    return out


def _input_scopes(task: Task) -> list[tuple[str, str]]:
    """`company.yaml > workspace.org_units` -> ("company.yaml", "workspace.org_units")."""
    scopes = []
    for item in task.inputs:
        m = re.match(r"^`?(?P<file>[\w./-]+\.ya?ml)`?(?:\s*>\s*`?(?P<prefix>[\w.\-\[\]]+)`?)?", item)
        if m:
            scopes.append((m.group("file"), m.group("prefix") or ""))
    return scopes


def _gate_applies(gate: str, task: Task, tasks: dict[str, Task]) -> bool:
    chain = {task.id} | ancestors(tasks, task.id)
    if "-" in gate:  # a task or spike id
        return gate in chain
    # A track gate (T1) applies to every task in or after that track's tasks.
    return any(tasks[t].track_id == gate for t in chain)


def _covers(prefix: str, path: str) -> bool:
    return not prefix or path == prefix or path.startswith(prefix + ".") or path.startswith(prefix + "[")


def required_for(task: Task, tasks: dict[str, Task], reqs: list[Required]) -> list[Required]:
    """The required values task `task` needs.

    - Marker gated on a task or track (`REQUIRED before T1`): needed by that
      task or track and everything that depends on it.
    - Marker with a free-text qualifier (`REQUIRED before any template is
      sendable`): needed only by tasks whose Inputs name its section explicitly.
    - Bare marker: needed by tasks whose Inputs name its file or section.
    """
    scopes = _input_scopes(task)
    out = []
    for r in reqs:
        if r.gate:
            if _gate_applies(r.gate, task, tasks):
                out.append(r)
        elif r.note:
            if any(f == r.file and p and _covers(p, r.path) for f, p in scopes):
                out.append(r)
        elif any(f == r.file and _covers(p, r.path) for f, p in scopes):
            out.append(r)
    return out


def _cross_reference(root: Path, company: dict[str, Any], docs: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    users = (docs.get("users") or {}).get("users") or []
    groups = (docs.get("groups") or {}).get("groups") or []
    roles = (docs.get("roles") or {}).get("roles") or []
    send_as = (docs.get("send_as") or {}).get("send_as") or {}
    user_ids = {u.get("id") for u in users}
    group_names = {g.get("name") for g in groups}
    role_names = {r.get("name") for r in roles}
    ufile, gfile = company["files"].get("users", "users"), company["files"].get("groups", "groups")

    seen: set[str] = set()
    for g in groups:
        name = g.get("name")
        if name in seen:
            errors.append(f"{gfile}: group {name} defined twice")
        seen.add(name)
        kind = g.get("kind")
        if kind == "access" and not str(name).startswith("grp-"):
            errors.append(f"{gfile}: access group {name} must start with grp-")
        if kind == "mail" and str(name).startswith(("grp-", "role-")):
            errors.append(f"{gfile}: mail group {name} must not use the grp- or role- prefix")
        for m in g.get("members") or []:
            if m not in user_ids:
                errors.append(f"{gfile}: group {name} member {m} is not a user id in {ufile}")
    for u in users:
        uid = u.get("id")
        for r in u.get("roles") or []:
            if r not in role_names:
                errors.append(f"{ufile}: user {uid} has unknown role {r}")
        for g in u.get("access_groups") or []:
            if g not in group_names:
                errors.append(f"{ufile}: user {uid} access group {g} not in {gfile}")
        ou = u.get("org_unit")
        if ou and ou not in company["workspace"].get("org_units", []):
            errors.append(f"{ufile}: user {uid} org unit {ou} not in company.yaml > workspace.org_units")
    for svc in users:
        if svc.get("primary") == company["workspace"].get("service_user") and svc.get("super_admin"):
            errors.append(f"{ufile}: the service user must not be a super administrator")
    admins = set(company["workspace"].get("admin_accounts", []))
    for a in admins - {u.get("primary") for u in users}:
        errors.append(f"{ufile}: administrator account {a} from company.yaml has no user entry")
    sfile = company["files"].get("send_as", "send_as")
    for uid, addrs in send_as.items():
        if uid not in user_ids:
            errors.append(f"{sfile}: unknown user id {uid}")
        for a in addrs or []:
            if a not in group_names:
                errors.append(f"{sfile}: {uid} sends as {a}, which is not a group in {gfile}")
    return errors


def validate(root: Path, for_task: str | None = None) -> tuple[list[str], list[Required]]:
    """Return (errors, required values still empty)."""
    errors: list[str] = []
    try:
        company = load_company(root)
    except BoxError as exc:
        return [str(exc)], []
    schema = json.loads((root / SCHEMA_FILE).read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(company), key=lambda e: list(e.absolute_path)):
        where = ".".join(str(p) for p in err.absolute_path) or "(top level)"
        errors.append(f"{COMPANY_FILE} > {where}: {err.message}")
    if errors:
        return errors, []

    docs: dict[str, Any] = {}
    for key, rel in (company.get("files") or {}).items():
        try:
            docs[key] = load_yaml(root / rel)
        except BoxError as exc:
            errors.append(f"files.{key}: {exc}")
    for key in ("legal",):
        for field in ("catalogue", "packages", "dictionary_seed"):
            rel = company[key].get(field)
            if rel and not (root / rel).is_file():
                errors.append(f"{COMPANY_FILE} > {key}.{field}: {rel} not found")
    if errors:
        return errors, []
    errors.extend(_cross_reference(root, company, docs))

    missing: list[Required] = []
    if for_task:
        tasks = load_tasks(root)
        if for_task not in tasks:
            errors.append(f"unknown task {for_task}")
        else:
            missing = [r for r in required_for(tasks[for_task], tasks, all_required(root, company)) if r.empty]
    return errors, missing
