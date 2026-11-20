# Company in a box

A repository that stands up a company's operating system on Google
Workspace and is executed task by task by Claude Code.

- Specification: `docs/SPEC.md`
- Working instructions for Claude Code: `CLAUDE.md`
- Tasks: `tasks/INDEX.md` (63 tasks) and `spikes/` (4 test tasks)
- This deployment's values: `company.yaml`, `directory/`, `drive/`, `content/`
- Inputs still needed from the owner: `content/inputs-required.md`

## Bootstrap order

1. Fill the REQUIRED values in `company.yaml` and `directory/users.yaml`
   that the next task needs (`box validate --for <task>` lists them).
2. T0: repository, validation, Google Cloud project, pipeline.
3. T1: tenant checklist (manual), users, groups, send-as, baseline check.
4. T2 and T3 in parallel: DNS and mail; drives, folders, register.
5. Spikes S-01, S-02, S-03. Stop if any fails.
6. T4 cockpit core, then T5, T6, T7, T8.
7. T9 to T12.
8. T13 when everything else has passed.

## What is not code

Manual console steps are in `runbooks/00-bootstrap.md`. Assistants are
built by hand from `assistants/`. Both are tracked as setup steps with
evidence.
