# Working instructions for Claude Code

Read `docs/SPEC.md` first. It governs. Then work through `tasks/` in
dependency order.

## Order of work

1. Run `box validate`. Stop if it fails and report the empty required values.
2. Pick the lowest-numbered task whose `Depends on` tasks are all `DONE` in
   `setup-status.json`.
3. Do the task's steps. Run its exit criteria. Write its evidence.
4. Set the task to `DONE` only when every exit criterion passes.
5. Commit with the task ID in the message. One task per commit.

## Stop and report

Stop, do not improvise, when:

- A step is listed under `Human steps`. Print the step, the expected value
  and where evidence goes, then wait.
- A required value in `company.yaml` or `directory/` is empty.
- A spike's answer is no, or differs from what the dependent task assumes.
- An action would touch the live tenant and `workspace.environment` is not
  `test`, unless the task says `Live: allowed`.
- An exit criterion fails twice.

## Rules

- Design rules R1 to R10 in the specification apply to every change.
- Never write a company name, domain, address or person's name outside
  `company.yaml`, `directory/`, `drive/` and `content/`. Run
  `box check-literals` before each commit.
- Never store or log a field marked `never_store`.
- Never add a dependency that is not included in the Workspace
  subscription or free from Google. Never call a Gemini API from code.
- Never grant super-administrator rights to the service user.
- Register access goes through `engine/cockpit/data.js` only.
- `Events` rows are appended, never changed.
- Every script must be safe to run twice.
- Do not edit `docs/SPEC.md` to make a task pass. Propose the change in
  `docs/spec-changes.md` and stop.

## Environments

`workspace.environment` is `test` or `live`. Build and verify each task on
the test tenant. A task is applied to the live tenant only after it is
`DONE` on test and the owner has approved the pull request.

## Evidence

Each task writes to `setup-status.json`: status, commit, time, and a link
or path to its evidence. Once the cockpit exists, the same goes to the
`Setup` tab.
