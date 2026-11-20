"""Entry point for the `box` command."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from .literals import CHECKED_DIRS, EXEMPT_MARKER, check_literals
from .repo import BoxError, find_root, load_company
from .runbook import PLACEHOLDER_RE, render_all
from .status import STATUS_FILE, load_status, mark_done, runnable, status_of
from .tasks import load_tasks, sort_key
from .validate import all_required, required_for
from .validate import validate as run_validate

app = typer.Typer(
    help="Company-in-a-box: configuration, status and setup tooling.",
    no_args_is_help=True,
    add_completion=False,
)

RootOption = typer.Option(None, "--root", help="Repository root. Default: $BOX_ROOT or the nearest parent with company.yaml.")


def _root(root: Optional[Path]) -> Path:
    try:
        return find_root(root)
    except BoxError as exc:
        typer.secho(f"error: {exc}", fg="red", err=True)
        raise typer.Exit(2) from None


@app.command()
def validate(
    for_task: Optional[str] = typer.Option(None, "--for", help="Also fail on empty REQUIRED values this task needs."),
    root: Optional[Path] = RootOption,
) -> None:
    """Validate company.yaml and every file it references."""
    base = _root(root)
    try:
        errors, missing = run_validate(base, for_task)
    except BoxError as exc:
        errors, missing = [str(exc)], []
    for e in errors:
        typer.secho(f"error: {e}", fg="red", err=True)
    for r in missing:
        when = f" ({'before ' + r.gate if r.gate else r.note})" if (r.gate or r.note) else ""
        typer.secho(f"required: {r.file} > {r.path} is empty{when}  [{r.file}:{r.line}]", fg="yellow", err=True)
    if errors or missing:
        typer.echo(f"validate: FAILED ({len(errors)} errors, {len(missing)} empty required values)", err=True)
        raise typer.Exit(1)
    typer.echo("validate: OK" + (f" for {for_task}" if for_task else ""))


@app.command("check-literals")
def check_literals_cmd(root: Optional[Path] = RootOption) -> None:
    """Fail if a company value or person's name appears outside the data paths (rule R1)."""
    base = _root(root)
    try:
        hits = check_literals(base)
    except BoxError as exc:
        typer.secho(f"error: {exc}", fg="red", err=True)
        raise typer.Exit(2) from None
    for h in hits:
        typer.secho(f"{h.path}:{h.line}: contains {h.literal!r}: {h.text[:120]}", fg="red", err=True)
    if hits:
        typer.echo(
            f"check-literals: FAILED ({len(hits)} lines). Move the value to company.yaml or mark the line `{EXEMPT_MARKER}`.",
            err=True,
        )
        raise typer.Exit(1)
    typer.echo(f"check-literals: OK ({', '.join(CHECKED_DIRS)})")


def _fail(exc: BoxError) -> None:
    typer.secho(f"error: {exc}", fg="red", err=True)
    raise typer.Exit(1)


@app.command()
def status(root: Optional[Path] = RootOption) -> None:
    """Every task and spike by track, with status, and the next runnable tasks."""
    base = _root(root)
    try:
        tasks = load_tasks(base)
        data = load_status(base)
        reqs = all_required(base, load_company(base))
    except BoxError as exc:
        _fail(exc)
    by_track: dict[str, list] = {}
    for t in sorted(tasks.values(), key=lambda t: sort_key(t.id)):
        by_track.setdefault(t.track, []).append(t)
    colours = {"DONE": "green", "FAILED": "red", "DRIFTED": "red", "IN_PROGRESS": "cyan", "WAITING_ON_INPUT": "yellow"}
    for track, items in by_track.items():
        done = sum(status_of(data, t.id) == "DONE" for t in items)
        typer.secho(f"\n{track}  ({done}/{len(items)} done)", bold=True)
        for t in items:
            st = status_of(data, t.id)
            human = "  [human step]" if t.human_steps else ""
            typer.echo(f"  {t.id:<7} " + typer.style(f"{st:<16}", fg=colours.get(st)) + f" {t.title}{human}")
    nxt = runnable(tasks, data)
    typer.secho("\nNext runnable", bold=True)
    if not nxt:
        typer.echo("  none")
    for t in nxt:
        missing = [r for r in required_for(t, tasks, reqs) if r.empty]
        notes = []
        if missing:
            notes.append("needs input: " + ", ".join(f"{r.file} > {r.path}" for r in missing))
        if t.human_steps:
            notes.append("human step")
        typer.echo(f"  {t.id:<7} {t.title}" + (f"  ({'; '.join(notes)})" if notes else ""))
    total = sum(status_of(data, t) == "DONE" for t in tasks)
    typer.echo(f"\n{total}/{len(tasks)} done. Store: {STATUS_FILE}")


@app.command()
def done(
    task_id: str = typer.Argument(..., help="Task or spike id, e.g. T0-02."),
    evidence: str = typer.Option(..., "--evidence", help="Path in the repository or URL of the evidence."),
    commit: Optional[str] = typer.Option(None, "--commit", help="Commit the evidence refers to. Default: HEAD."),
    root: Optional[Path] = RootOption,
) -> None:
    """Mark a task DONE. Refused while any dependency is not DONE."""
    base = _root(root)
    try:
        entry = mark_done(base, load_tasks(base), task_id, evidence, commit)
    except BoxError as exc:
        _fail(exc)
    typer.echo(f"{task_id}: DONE at {entry['time']} (commit {entry['commit'][:12] or 'none'}, evidence {entry['evidence']})")


@app.command()
def runbook(root: Optional[Path] = RootOption) -> None:
    """Render runbooks/*.md with values from company.yaml into runbooks/rendered/."""
    base = _root(root)
    try:
        written, errors = render_all(base)
    except BoxError as exc:
        _fail(exc)
    for path in written:
        leftover = PLACEHOLDER_RE.findall(path.read_text(encoding="utf-8"))
        if leftover:
            errors.append(f"{path.relative_to(base)}: unresolved placeholders {sorted(set(leftover))}")
        typer.echo(f"wrote {path.relative_to(base)}")
    for e in errors:
        typer.secho(f"error: {e}", fg="red", err=True)
    if errors:
        raise typer.Exit(1)


if __name__ == "__main__":  # pragma: no cover
    app()
