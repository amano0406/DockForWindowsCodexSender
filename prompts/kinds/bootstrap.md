# Codex Task: Repository bootstrap and safe status check

{{ common.send_verification_block }}

You are working in repository:

```text
{{ repo.name }}
```

Repository path:

```text
{{ repo.path }}
```

Product family:

```text
{{ repo.product_family }}
```

Priority:

```text
{{ repo.priority }}
```

## Common operating context

{{ common.timeline_operating_context }}

## Product-specific note

{{ product_note }}

## Task

Start with a non-destructive repository bootstrap and status check.

Perform the following in order:

1. Inspect the repository structure.
2. Check whether `AGENTS.md` exists.
3. If `AGENTS.md` is missing, report that it is missing. Do not create it from this bootstrap prompt.
4. If `AGENTS.md` exists, inspect it but update it only if the user explicitly requested AGENTS maintenance.
5. Inspect README, docs, config, Docker, CLI, tests, and scripts.
6. Check whether fixed input/output/state directory policy is documented or implemented.
7. Check whether Job and Run concepts are mixed.
8. Check whether raw input files could be deleted, overwritten, or mass-renamed.
9. Check whether Docker/Web UI ports are localhost-bound when applicable.
10. Make only safe, non-destructive improvements.
11. Run available lightweight tests or smoke checks if practical.
12. Do not perform destructive changes.

## Do not do

- Do not delete raw input.
- Do not mass rename or move raw input.
- Do not deploy.
- Do not modify secrets.
- Do not perform external posting.
- Do not perform broad architecture rewrites.
- Do not break output contracts.
- Do not rename the product or repository.
- Do not create `AGENTS.md`; use the separate `agents_update` prompt kind when AGENTS maintenance is explicitly requested.

## Report format

Return:

```md
Run ID: <echo the run id above>

## Current state

## Completed

## Changed files

## Fixed input/output policy check

## Job / Run model check

## Docker / port / security check

## Tests

## Risks

## Next safe tasks

## Human decisions needed
```
