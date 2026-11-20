import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

REPO = Path(__file__).resolve().parents[1]
COPY = ["company.yaml", "schema", "directory", "drive", "defaults", "content", "tasks", "spikes", "runbooks", "docs", "assistants"]


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A throwaway copy of the repository's configuration and task files."""
    for name in COPY:
        src = REPO / name
        if src.is_dir():
            shutil.copytree(src, tmp_path / name, ignore=shutil.ignore_patterns("rendered"))
        elif src.exists():
            shutil.copy2(src, tmp_path / name)
    (tmp_path / "engine").mkdir()
    return tmp_path


@pytest.fixture
def run(repo: Path):
    from box.main import app

    runner = CliRunner()

    def _run(*args: str):
        return runner.invoke(app, [*args, "--root", str(repo)])

    return _run
