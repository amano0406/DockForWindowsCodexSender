# Codex Task: Fixed input/output directory and Job/Run check

{{ common.send_verification_block }}

You are working in repository:

```text
{{ repo.name }}
```

## Common operating context

{{ common.timeline_operating_context }}

## Product-specific note

{{ product_note }}

## Task

Check how this repository handles input, output, state, jobs, and runs.

Focus on:

- fixed input directory
- fixed output directory
- state directory
- raw input protection
- input snapshot
- Job vs Run separation
- artifact output structure
- `.env.example`
- Docker volume mapping
- localhost bind

Make only safe, non-destructive changes.

Do not implement large architecture changes. If needed, propose them instead.

Report:

```md
Run ID: <echo the run id above>

## Current model

## Problems

## Safe changes made

## Proposed larger changes

## Tests

## Human decisions needed
```
