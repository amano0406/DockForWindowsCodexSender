# ADR-0001: Send-only first

## Status

Accepted.

## Decision

Start `DockForWindowsCodexSender` as a CLI-only, send-only bridge.

v0.1 supports:

- repository registry
- prompt rendering
- outbox prompt files
- dry-run
- Docker-wrapped Codex CLI send
- send logs
- prompt-side verification metadata for reconciliation

v0.1 does not support:

- response scraping
- first-party Web UI or dashboard
- browser frontend
- local web service
- Docker Compose web stack
- Windows app UI automation
- autonomous scheduling
- automatic merge
- automatic evaluation

## Rationale

Sending prompts safely is the immediate bottleneck.

Receiving and analysis can be handled later by `TimelineForWindowsCodex`.

Web UI and UI automation would add maintenance and verification cost without improving the v0.1 send-only goal.
Windows app UI may still be used for human inspection, but it is outside this product boundary. CLI logs and artifacts remain the primary evidence path.

Normal CLI execution is Docker-only. Host-side CLI execution is blocked by default and is available only for explicit test/debug exceptions through `DOCK_CODEX_ALLOW_HOST_CLI=1`.
