# Project Context

`DockForWindowsCodexSender` is a small send-only bridge for local Windows Codex operations.

It exists because multiple Timeline/Dock/Tool product repositories need repeated Codex prompts, but manual copy/paste across many repositories is operationally expensive.

## Key decision

Start with Codex CLI transport rather than Windows app UI automation.

## Why

- CLI is scriptable.
- CLI dry-run behavior is easier to reason about.
- Sending logs are easier to preserve.
- Prompt artifacts can carry verification metadata such as `run_id` and `prompt_sha256`.
- Windows app UI automation has focus, IME, selector, thread-targeting, and UI-change risks.

Windows app UI still matters for human visual management, but it is not the primary evidence source for sent content or changed files.

## Relationship to related products

```text
DockForWindowsCodexSender
  = send-only prompt bridge

TimelineForWindowsCodex
  = future receive/analyze/timeline product

ToolForAgentOps
  = future higher-level evaluation / approval / growth loop
```
