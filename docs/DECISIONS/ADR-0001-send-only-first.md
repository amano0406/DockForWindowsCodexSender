# ADR-0001: Send-only first

## Status

Accepted.

## Decision

Start `DockForWindowsCodexSender` as a send-only bridge.

v0.1 supports:

- repository registry
- prompt rendering
- outbox prompt files
- dry-run
- Codex CLI send
- send logs
- prompt-side verification metadata for reconciliation

v0.1 does not support:

- response scraping
- Windows app UI automation
- autonomous scheduling
- automatic merge
- automatic evaluation

## Rationale

Sending prompts safely is the immediate bottleneck.

Receiving and analysis can be handled later by `TimelineForWindowsCodex`.

UI automation is useful but riskier than CLI transport, so it should not be the first implementation target.
Windows app UI may still be used for human inspection, but CLI logs and artifacts remain the primary evidence path.
