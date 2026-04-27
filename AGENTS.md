# AGENTS.md

## Project role

This repository is `DockForWindowsCodexSender`.

It is a send-only bridge/tool for preparing and sending prompts to local Windows Codex / Codex CLI workflows.

It is not a Timeline product. It supports Timeline/Dock/Tool product operations by:

- managing target repository registry
- rendering prompt templates
- generating per-product Codex instructions
- dry-running send operations
- sending approved prompts via Codex CLI
- recording send logs

Receiving, thread analysis, and long-term status extraction are out of scope for v0.1 and can be handled later by `TimelineForWindowsCodex`.

Operational stance:

- treat Codex CLI send as the primary automation and evidence path
- treat Windows app UI as useful for visual management, not primary evidence
- do not assume CLI sends are visible in Windows app UI until verified
- use send log, prompt artifacts, transcript, and `TimelineForWindowsCodex` for later receive-side organization
- keep Windows app UI automation as the last resort

## Primary objective for v0.1

Build the smallest safe system that can:

1. read configured repositories
2. render prompt templates
3. produce outbox prompt files
4. dry-run send operations
5. send one prompt to one target repo through Codex CLI
6. record what was sent

Do not implement Windows Codex app UI automation in v0.1 unless explicitly requested later.

## Non-goals for v0.1

Do not build:

- autonomous agent operation
- automatic thread reading
- Windows app UI automation
- automatic merge
- cloud deploy
- external posting
- raw file management
- full AgentOps evaluation loop

## Safety principles

Follow these strictly.

1. Send-only first.
2. Dry-run before actual send.
3. One target repo before send-all.
4. Log every rendered and sent prompt.
5. Do not delete, rename, or move raw input files.
6. Do not change secrets.
7. Do not deploy.
8. Do not merge automatically.
9. Do not expose web services publicly.
10. Prefer Codex CLI over Windows app UI automation.
11. Do not treat Windows app UI as the sole proof of sent content or file changes.

## Codex transport policy

Use this priority order:

1. `codex exec` through Codex CLI
2. manual copy/paste prompt files
3. Windows app UI for human monitoring and thread inspection
4. Windows Codex app UI automation only as a future optional adapter

The CLI transport should support dry-run and should not run unless explicitly requested.

## Repository layout

Expected layout:

```text
config/
  repos.example.yaml
  repos.yaml
  prompts.yaml

prompts/
  common/
  kinds/
  products/
  codex-thread/

data/
  outbox/
  sent/
  logs/

src/
  dock_for_windows_codex_sender/

tests/
```

## Commands to support

Minimum useful commands:

```bash
dock-windows-codex-sender repos list
dock-windows-codex-sender prompt render --repo <repo_id> --kind <kind>
dock-windows-codex-sender prompt render-all --kind <kind>
dock-windows-codex-sender send --repo <repo_id> --kind <kind> --dry-run
dock-windows-codex-sender send --repo <repo_id> --kind <kind>
dock-windows-codex-sender send-all --kind <kind> --dry-run
```

Actual send-all without dry-run should require an explicit confirmation flag.

## Work allowed without further confirmation

You may do the following:

- create or update docs
- create or update prompt templates
- implement CLI scaffolding
- implement dry-run behavior
- implement Codex CLI send adapter
- add tests
- update `.env.example`
- update `config/*.example.yaml`
- create basic scripts
- improve error messages
- run local tests

## Work requiring confirmation

Ask before doing any of these:

- Windows app UI automation
- automatic response scraping
- automatic scheduling
- automatic merge
- repository rename
- destructive migration
- secret modification
- deploy
- external posting
- broad send-all execution without dry-run
- sending prompts that may modify many target repos

## Reporting format

After work, report using this format:

```md
## Current state

## Completed

## Changed files

## Tests

## Dry-run / send behavior

## Risks

## Next safe tasks

## Human decisions needed
```

## Design priority

When tradeoffs arise, prioritize:

1. safety
2. dry-run visibility
3. clear logs
4. simple CLI
5. reproducible prompt rendering
6. Codex CLI transport
7. future extensibility
