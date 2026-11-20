"""Task and spike files: front matter, inputs and the dependency graph."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .repo import BoxError

TASK_DIRS = ("tasks", "spikes")
_ID_RE = re.compile(r"^(?:T(\d+)-(\d+)|S-(\d+))$")


@dataclass
class Task:
    id: str
    title: str
    track: str
    priority: str
    depends_on: list[str]
    path: Path
    inputs: list[str] = field(default_factory=list)
    human_steps: list[str] = field(default_factory=list)

    @property
    def track_id(self) -> str:
        """`T1` for T1-03, `S` for spikes."""
        return self.id.split("-")[0] if self.id.startswith("T") else "S"


def sort_key(task_id: str) -> tuple[int, int, int]:
    """Lowest-numbered first: tracks in number order; spikes after T3, as in the bootstrap order."""
    m = _ID_RE.match(task_id)
    if not m:
        return (999, 999, 999)
    if m.group(3):
        return (3, 1, int(m.group(3)))
    return (int(m.group(1)), 0, int(m.group(2)))


def _sections(body: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    current = None
    for line in body.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            out[current] = []
        elif current and line.startswith("- "):
            out[current].append(line[2:].strip())
    return out


def parse_task(path: Path) -> Task:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise BoxError(f"{path}: missing front matter")
    try:
        _, front, body = text.split("---\n", 2)
        meta = yaml.safe_load(front) or {}
    except (ValueError, yaml.YAMLError) as exc:
        raise BoxError(f"{path}: bad front matter: {exc}") from None
    for key in ("id", "title", "track", "depends_on"):
        if key not in meta:
            raise BoxError(f"{path}: front matter lacks `{key}`")
    sections = _sections(body)
    human = [s for s in sections.get("Human steps", []) if s.rstrip(".").lower() != "none"]
    return Task(
        id=str(meta["id"]),
        title=str(meta["title"]),
        track=str(meta["track"]),
        priority=str(meta.get("priority", "")),
        depends_on=[str(d) for d in meta["depends_on"] or []],
        path=path,
        inputs=sections.get("Inputs", []),
        human_steps=human,
    )


def load_tasks(root: Path) -> dict[str, Task]:
    """Load every task and spike; fail on duplicate, unknown or cyclic dependencies."""
    tasks: dict[str, Task] = {}
    for d in TASK_DIRS:
        for path in sorted((root / d).glob("*.md")):
            if path.name == "INDEX.md":
                continue
            task = parse_task(path)
            if task.id in tasks:
                raise BoxError(f"duplicate task id {task.id} in {path} and {tasks[task.id].path}")
            tasks[task.id] = task
    check_graph(tasks)
    return tasks


def check_graph(tasks: dict[str, Task]) -> None:
    errors = []
    for t in tasks.values():
        for dep in t.depends_on:
            if dep not in tasks:
                errors.append(f"{t.id} depends on unknown task {dep}")
    if errors:
        raise BoxError("; ".join(errors))
    state: dict[str, int] = {}  # 1 visiting, 2 done

    def visit(node: str, trail: list[str]) -> None:
        if state.get(node) == 2:
            return
        if state.get(node) == 1:
            cycle = trail[trail.index(node):] + [node]
            raise BoxError("dependency cycle: " + " -> ".join(cycle))
        state[node] = 1
        for dep in tasks[node].depends_on:
            visit(dep, trail + [node])
        state[node] = 2

    for tid in sorted(tasks, key=sort_key):
        visit(tid, [])


def ancestors(tasks: dict[str, Task], task_id: str) -> set[str]:
    """Every task that `task_id` depends on, directly or transitively."""
    seen: set[str] = set()
    stack = list(tasks[task_id].depends_on)
    while stack:
        dep = stack.pop()
        if dep not in seen:
            seen.add(dep)
            stack.extend(tasks[dep].depends_on)
    return seen
