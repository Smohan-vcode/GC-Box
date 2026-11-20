# box

Command-line tool for this repository. Python 3.12, Typer.

## Install

```bash
uv venv --python 3.12 .venv && uv pip install --python .venv -e ".[dev]"
source .venv/bin/activate
```

## Commands

| Command | Does |
| --- | --- |
| `box validate` | Validates `company.yaml` against `schema/company.schema.json`, loads every file under `files`, and cross-checks users, groups, roles and send-as. |
| `box validate --for <task>` | Also fails on empty values marked `# REQUIRED` that the task needs. |
| `box status` | Every task and spike by track with its status, and the next runnable tasks with any missing input. |
| `box done <id> --evidence <path-or-url>` | Marks a task DONE in `setup-status.json` with commit, time and evidence. Refused while a dependency is not DONE. |
| `box runbook` | Renders `runbooks/*.md` with values from `company.yaml` into `runbooks/rendered/`. Fails on an unknown placeholder. |
| `box check-literals` | Rule R1: fails if a company value or a person's full name appears under `engine/`, `defaults/`, `tasks/`, `spikes/`, `assistants/` or `docs/`. A line containing `example:` is exempt. |

The repository root is `--root`, else `$BOX_ROOT`, else the nearest parent
directory holding `company.yaml`.

## Required markers

A value is required when its line carries a `# REQUIRED` comment:

| Marker | Needed by |
| --- | --- |
| `# REQUIRED before T1` | Every task in track T1, and every task that depends on one |
| `# REQUIRED before T9-02` | T9-02 and every task that depends on it |
| `# REQUIRED before <anything else>` | Tasks whose Inputs name the value's section, e.g. `company.yaml > data` |
| `# REQUIRED` or `# REQUIRED: <description>` | Tasks whose Inputs name the file or section |

A bare `# REQUIRED` inherits the qualifier of the marker above it in the
same block.

## Tests

```bash
pytest
```

The bootstrap order is in the repository README.
