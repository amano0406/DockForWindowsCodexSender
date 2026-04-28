# Codex Task: Timeline next repository check

{{ common.send_verification_block }}

You are working in repository:

```text
{{ repo.name }}
```

Repository path:

```text
{{ repo.path }}
```

## First, read

Read these before deciding what to do:

- `AGENTS.md`
- `README.md` and related docs
- relevant config, Docker, scripts, CLI, worker, web, and tests

Treat `AGENTS.md` as the operating rule for this repo.

## Common operating context

{{ common.timeline_operating_context }}

## Product-specific focus

{{ product_note }}

## Task

Do a non-destructive next-step check for this Timeline product.

1. Inspect the current repo state.
2. Confirm that `AGENTS.md` exists and is consistent with the actual repo.
3. Check README/docs/config/scripts/tests against `AGENTS.md`.
4. Decide the next low-risk work that should be done now.
5. Proceed without stopping on read-only checks, reversible investigation, local tests, and small non-destructive fixes.
6. If an error occurs, investigate the cause, check relevant docs/code/tests, try a low-risk fix, and retry up to 2-3 times when practical.
7. Report only unresolved issues that require human judgment.

## Do not do

- Do not delete, overwrite, mass move, or mass rename original/source data.
- Do not modify secrets.
- Do not deploy.
- Do not post externally.
- Do not break output/export contracts.
- Do not rename the repo or product.
- Do not make broad architecture rewrites.
- Do not add hosted/cloud dependencies without explicit approval.

## Report format

Return:

```md
Run ID: <echo the run id above>

## Current state

## Completed

## Changed files

## Product-specific contract check

## Output/export contract check

## Docker / port / security check

## Tests

## Risks

## Next safe tasks

## Human decisions needed
```
