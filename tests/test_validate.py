import re
from pathlib import Path

import yaml


def _edit(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    assert old in text, old
    path.write_text(text.replace(old, new, 1))


def test_repository_config_is_valid(run):
    result = run("validate")
    assert result.exit_code == 0, result.output
    assert "validate: OK" in result.output


def test_missing_primary_domain_fails_and_names_key(repo, run):
    _edit(repo / "company.yaml", re.search(r"  primary_domain: .*\n", (repo / "company.yaml").read_text()).group(0), "")
    result = run("validate")
    assert result.exit_code == 1
    assert "primary_domain" in result.output


def test_bad_enum_fails(repo, run):
    _edit(repo / "company.yaml", 'environment: "test"', 'environment: "staging"')
    result = run("validate")
    assert result.exit_code == 1
    assert "workspace.environment" in result.output


def test_referenced_file_missing_fails(repo, run):
    (repo / "directory" / "send-as.yaml").unlink()
    result = run("validate")
    assert result.exit_code == 1
    assert "send-as.yaml" in result.output


def test_unknown_group_reference_fails(repo, run):
    _edit(repo / "directory" / "send-as.yaml", "[sales,", "[no-such-group,")
    result = run("validate")
    assert result.exit_code == 1
    assert "no-such-group" in result.output


def test_for_task_without_requirements_passes(run):
    assert run("validate", "--for", "T0-01").exit_code == 0


def test_for_task_reports_track_gated_value(run):
    result = run("validate", "--for", "T1-01")
    assert result.exit_code == 1
    assert "workspace.test_domain" in result.output


def test_for_task_reports_values_named_in_inputs(run):
    result = run("validate", "--for", "T1-02")
    assert result.exit_code == 1
    assert "users[founder].primary" in result.output


def test_for_task_passes_once_values_filled(repo, run):
    _edit(repo / "company.yaml", 'test_domain: ""', 'test_domain: "test.invalid"')
    users = repo / "directory" / "users.yaml"
    _edit(users, 'primary: ""', 'primary: "first"')
    _edit(users, 'given_name: ""', 'given_name: "Given"')
    _edit(users, 'family_name: ""', 'family_name: "Family"')
    result = run("validate", "--for", "T1-02")
    assert result.exit_code == 0, result.output


def test_task_specific_gate_only_applies_downstream(run):
    out_before = run("validate", "--for", "T9-01").output
    out_at = run("validate", "--for", "T9-02").output
    assert "order_system.base_url" not in out_before
    assert "order_system.base_url" in out_at


def test_unknown_task(run):
    result = run("validate", "--for", "T99-01")
    assert result.exit_code == 1
    assert "unknown task" in result.output
