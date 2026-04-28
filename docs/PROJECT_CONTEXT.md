# Project Context

`DockForWindowsCodexSender` is a small send-only bridge for local Windows Codex operations.

It exists because multiple Timeline/Dock/Tool product repositories need repeated Codex prompts, but manual copy/paste across many repositories is operationally expensive.

## Key decision

Keep the product CLI-only and use Docker-wrapped Codex CLI transport rather than any Web UI or Windows app UI automation.

Windows PowerShell is the front door for normal operation. WSL/bash wrappers remain available as a back-door route for WSL-based automation or troubleshooting, but they are not the primary user-facing path.

## Why

- Docker-wrapped CLI is scriptable while keeping host Python/PATH out of the runtime contract.
- CLI dry-run behavior is easier to reason about.
- Sending logs are easier to preserve.
- Prompt artifacts can carry verification metadata such as `run_id` and `prompt_sha256`.
- A Web UI would add another surface to maintain without improving the send-only v0.1 goal.
- Windows app UI automation has focus, IME, selector, thread-targeting, and UI-change risks.

Windows app UI can still be checked manually by a human, but it is outside this product boundary and is not the primary evidence source for sent content or changed files.

## Relationship to related products

```text
DockForWindowsCodexSender
  = send-only prompt bridge

TimelineForWindowsCodex
  = future receive/analyze/timeline product

ToolForAgentOps
  = future higher-level evaluation / approval / growth loop
```
