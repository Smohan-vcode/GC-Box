"""The status store, `setup-status.json`, until the cockpit's Setup tab exists."""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .repo import BoxError
from .tasks import Task, sort_key

STATUS_FILE = "setup-status.json"
STATUSES = ("NOT_STARTED", "WAITING_ON_INPUT", "IN_PROGRESS", "DONE", "FAILED", "DRIFTED")
_URL_RE = re.compile(r"^https?://\S+$")


def load_status(root: Path) -> dict[str, Any]:
    path = root / STATUS_FILE
    if not path.is_file():
        return {"version": 1, "steps": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BoxError(f"{STATUS_FILE}: invalid JSON: {exc}") from None
    data.setdefault("steps", {})
    for sid, entry in data["steps"].items():
        if entry.get("status") not in STATUSES:
            raise BoxError(f"{STATUS_FILE}: {sid} has unknown status {entry.get('status')!r}")
    return data


def save_status(root: Path, data: dict[str, Any]) -> None:
    data["steps"] = dict(sorted(data["steps"].items(), key=lambda kv: sort_key(kv[0])))
    (root / STATUS_FILE).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def status_of(data: dict[str, Any], task_id: str) -> str:
    return data["steps"].get(task_id, {}).get("status", "NOT_STARTED")


def runnable(tasks: dict[str, Task], data: dict[str, Any]) -> list[Task]:
    """Tasks not DONE whose dependencies are all DONE, lowest-numbered first."""
    out = [
        t
        for t in tasks.values()
        if status_of(data, t.id) != "DONE" and all(status_of(data, d) == "DONE" for d in t.depends_on)
    ]
    return sorted(out, key=lambda t: sort_key(t.id))


def head_commit(root: Path) -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def mark_done(root: Path, tasks: dict[str, Task], task_id: str, evidence: str, commit: str | None = None) -> dict[str, Any]:
    if task_id not in tasks:
        raise BoxError(f"unknown task {task_id}")
    data = load_status(root)
    blocking = [d for d in tasks[task_id].depends_on if status_of(data, d) != "DONE"]
    if blocking:
        raise BoxError(f"{task_id} cannot be DONE: dependencies not DONE: {', '.join(blocking)}")
    if not evidence.strip():
        raise BoxError("evidence is required")
    if not _URL_RE.match(evidence) and not (root / evidence).exists():
        raise BoxError(f"evidence {evidence} is neither a URL nor a path in the repository")
    entry = {
        "status": "DONE",
        "commit": commit or head_commit(root),
        "time": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "evidence": evidence,
    }
    data["steps"][task_id] = entry
    save_status(root, data)
    return entry
