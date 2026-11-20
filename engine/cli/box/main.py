"""Entry point for the `box` command."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from .literals import CHECKED_DIRS, EXEMPT_MARKER, check_literals
from .repo import BoxError, find_root
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


if __name__ == "__main__":  # pragma: no cover
    app()
