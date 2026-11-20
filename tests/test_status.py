import json
import re

import pytest

from box.repo import BoxError
from box.tasks import load_tasks


def _write_task(repo, tid, deps):
    (repo / "tasks" / f"{tid}.md").write_text(
        f'---\nid: {tid}\ntitle: "t"\ntrack: "T0 Foundation"\npriority: P0\nsize: S\ndepends_on: {json.dumps(deps)}\n---\n\n## Inputs\n- None\n'
    )


def test_status_lists_every_task_and_spike(repo, run):
    result = run("status")
    assert result.exit_code == 0, result.output
    ids = [p.stem for d in ("tasks", "spikes") for p in (repo / d).glob("*.md") if p.name != "INDEX.md"]
    assert len(ids) == 67
    for tid in ids:
        assert re.search(rf"^\s+{re.escape(tid)}\s", result.output, re.M), tid
    assert "Next runnable" in result.output


def test_unknown_dependency_is_an_error(repo):
    _write_task(repo, "T0-99", ["T42-01"])
    with pytest.raises(BoxError, match="unknown task T42-01"):
        load_tasks(repo)


def test_cycle_is_an_error(repo):
    _write_task(repo, "T0-98", ["T0-99"])
    _write_task(repo, "T0-99", ["T0-98"])
    with pytest.raises(BoxError, match="cycle"):
        load_tasks(repo)


def test_done_out_of_order_is_refused(repo, run):
    result = run("done", "T0-02", "--evidence", "company.yaml")
    assert result.exit_code == 1
    assert "T0-01" in result.output
    assert not (repo / "setup-status.json").exists()


def test_done_in_order_records_entry(repo, run):
    assert run("done", "T0-01", "--evidence", "company.yaml", "--commit", "abc123").exit_code == 0
    assert run("done", "T0-02", "--evidence", "https://example.invalid/e", "--commit", "def456").exit_code == 0
    data = json.loads((repo / "setup-status.json").read_text())
    assert data["steps"]["T0-01"]["status"] == "DONE"
    assert data["steps"]["T0-01"]["commit"] == "abc123"
    assert data["steps"]["T0-02"]["evidence"].startswith("https://")
    assert "T0-01" not in run("status").output.split("Next runnable")[1]


def test_done_requires_existing_evidence(repo, run):
    result = run("done", "T0-01", "--evidence", "no/such/file.txt")
    assert result.exit_code == 1
    assert "neither a URL nor a path" in result.output


def test_done_is_repeatable(repo, run):
    for _ in range(2):
        assert run("done", "T0-01", "--evidence", "company.yaml", "--commit", "abc").exit_code == 0
    data = json.loads((repo / "setup-status.json").read_text())
    assert list(data["steps"]) == ["T0-01"]


def test_runbook_renders_without_braces(repo, run):
    result = run("runbook")
    assert result.exit_code == 0, result.output
    text = (repo / "runbooks" / "rendered" / "00-bootstrap.md").read_text()
    assert not re.search(r"\{[a-z_][a-z0-9_.]*\}", text)
    assert "business_plus" in text


def test_runbook_unknown_placeholder_fails(repo, run):
    (repo / "runbooks" / "99-x.md").write_text("Value {no_such_key}\n")
    result = run("runbook")
    assert result.exit_code == 1
    assert "no_such_key" in result.output
