import yaml


def _company(repo):
    return yaml.safe_load((repo / "company.yaml").read_text())


def test_repository_passes(run):
    result = run("check-literals")
    assert result.exit_code == 0, result.output


def test_trading_name_under_engine_fails(repo, run):
    name = _company(repo)["company"]["trading_name"]
    (repo / "engine" / "x.js").write_text(f"const title = '{name} cockpit';\n")
    result = run("check-literals")
    assert result.exit_code == 1
    assert "engine/x.js:1" in result.output


def test_match_is_case_insensitive(repo, run):
    domain = _company(repo)["company"]["primary_domain"]
    (repo / "docs" / "note.md").write_text(f"mail ops@{domain.upper()}\n")
    assert run("check-literals").exit_code == 1


def test_example_line_is_exempt(repo, run):
    name = _company(repo)["company"]["trading_name"]
    (repo / "engine" / "x.md").write_text(f"example: {name}\n")
    assert run("check-literals").exit_code == 0


def test_data_paths_are_not_checked(repo, run):
    name = _company(repo)["company"]["trading_name"]
    (repo / "content" / "extra.md").write_text(f"{name}\n")
    assert run("check-literals").exit_code == 0


def test_person_full_name_fails(repo, run):
    users = repo / "directory" / "users.yaml"
    text = users.read_text().replace('given_name: ""', 'given_name: "Ada"', 1).replace('family_name: ""', 'family_name: "Quill"', 1)
    users.write_text(text)
    (repo / "defaults" / "x.yaml").write_text("owner: Ada Quill\n")
    assert run("check-literals").exit_code == 1
