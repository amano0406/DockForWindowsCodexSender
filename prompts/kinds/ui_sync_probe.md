# Codex Task: Sender and UI sync probe

{{ common.send_verification_block }}

You are working in repository:

```text
{{ repo.name }}
```

Repository path:

```text
{{ repo.path }}
```

## Purpose

This is a read-only verification probe for `DockForWindowsCodexSender`.

The goal is to verify that:

- a prompt can be sent through Codex CLI
- the run can later be reconciled by Run ID
- the repository is not modified by this probe

## Rules

- Read-only only.
- Do not edit files.
- Do not create commits, branches, or pushes.
- Do not install dependencies.
- Do not rename, move, or delete anything.

## Task

Perform only lightweight read-only checks:

1. Confirm the current working directory.
2. Inspect repository status in a minimal way.
3. State whether you made any file changes during this probe.
4. Echo the same Run ID exactly.

## Report format

Return:

```md
Run ID: <echo the run id above>

## Probe result

## Current working directory

## Repository status summary

## Files changed by this run
- none
```
