# DockForWindowsCodexSender

Send-only bridge for local Windows Codex operations.

This project starts small on purpose:

- Generate Codex prompts from templates.
- Render prompts per target repository.
- Dry-run before sending.
- Send prompts through Codex CLI when explicitly requested.
- Save rendered prompts, sent prompts, and send logs.
- Treat Windows app UI as a human-visible management surface, not the primary transport.
- Do **not** read or analyze Codex responses yet.
- Do **not** automate the Windows Codex app UI yet.

## Current scope

`DockForWindowsCodexSender` is not a Timeline product.

It is a Dock/Tool product whose first responsibility is:

```text
Prompt templates + repo registry
  -> render prompt
  -> save to outbox
  -> dry-run
  -> send via Codex CLI
  -> save sent copy
  -> record send log
```

Receiving and timeline analysis can be handled later by `TimelineForWindowsCodex`.

## Transport boundary

- CLI send is the primary path for automation and log preservation.
- Windows app UI is still useful for human visual/thread management.
- CLI send to app UI synchronization is not guaranteed in v0.1 and should be treated as a verification target, not an assumption.
- Receive-side organization is a later step using `send-log.jsonl`, transcript exports, and `TimelineForWindowsCodex`.
- Windows app UI automation remains the last resort.

## Install for development

```powershell
py -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## Configure repositories

```powershell
copy config\repos.example.yaml config\repos.yaml
```

Edit `config/repos.yaml` and set local repository paths.

If `config/repos.yaml` does not exist, the CLI falls back to `config/repos.example.yaml`.

## Prompt/config files

- `config/repos.yaml`: local repo registry
- `config/repos.example.yaml`: example repo registry and fallback
- `config/prompts.yaml`: prompt kind/profile mapping
- `prompts/kinds/*.md`: per-command templates
- `prompts/common/*.md`: shared context fragments
- `prompts/products/*.md`: product-specific notes

## Codex binary setup

If Codex CLI is installed on Windows and available on Windows `PATH`, the default `codex` is enough.

If Codex CLI exists only inside WSL, pass a launcher command string such as:

```powershell
set DOCK_CODEX_BIN=wsl.exe /mnt/c/Users/amano/.codex/bin/wsl/codex
```

`wsl.exe codex` alone may fail in non-interactive runs because the WSL shell `PATH` is not guaranteed to include `codex`.

## Basic commands

List configured repositories:

```powershell
dock-windows-codex-sender repos list
```

Render one prompt:

```powershell
dock-windows-codex-sender prompt render --repo timeline_for_chatgpt --kind bootstrap
```

If you want a human-chosen verification token, add `--run-id <token>`.

Render all bootstrap prompts to `data/outbox`:

```powershell
dock-windows-codex-sender prompt render-all --kind bootstrap
```

Dry-run send:

```powershell
dock-windows-codex-sender send --repo timeline_for_chatgpt --kind bootstrap --dry-run
```

Send into an existing Codex session:

```powershell
dock-windows-codex-sender send --repo timeline_for_chatgpt --kind bootstrap --resume 019dcbc7-fe5f-7ae3-8983-da7a703d9cf0
```

Resume the most recent session filtered by the target repo working directory:

```powershell
dock-windows-codex-sender send --repo timeline_for_chatgpt --kind bootstrap --resume-last
```

Read-only verification probe:

```powershell
dock-windows-codex-sender send --repo timeline_for_windows_codex --kind ui_sync_probe --run-id ui-probe-001 --dry-run
```

Dry-run prints:

- `repo_id`
- `kind`
- `run_id`
- `prompt_sha256`
- `status=dry-run`
- `outbox_path`
- the planned `codex exec ...` command

Resume notes:

- `--resume <session_id_or_name>` sends to an existing Codex session instead of creating a new one.
- `--resume-last` uses `codex exec resume --last` and relies on the target repo working directory for session filtering.
- Resume mode is available only on `send`, not on `send-all`, to avoid broad accidental posting into existing threads.

Actual send through Codex CLI:

```powershell
dock-windows-codex-sender send --repo timeline_for_chatgpt --kind bootstrap
```

Actual send behavior:

- Rendered prompt is always saved to `data/outbox`.
- Successful sends also save a copy to `data/sent`.
- Every dry-run/send appends one JSON line to `data/logs/send-log.jsonl`.
- Each prompt carries verification metadata in the body: `run_id`, `rendered_at`.
- CLI output and send logs also record `prompt_sha256`.
- When a real send creates or updates a `.codex/sessions/*.jsonl` file, CLI output and send logs also record `observed_thread_id` and `observed_session_path`.
- In resume mode, sender still writes a fresh outbox artifact before posting to the existing session.

## Verification stance

- Do not treat Windows Codex UI alone as the source of truth for what was sent.
- Use `run_id` to match the UI view with `data/outbox`, `data/sent`, and `data/logs/send-log.jsonl`.
- If available, use `observed_thread_id` and `observed_session_path` from `send-log.jsonl` as the direct bridge to local Codex transcript evidence.
- Use actual repo file diffs and test results as the source of truth for what changed.
- Treat CLI to Windows app UI visibility as a behavior to verify per environment.
- If you render and send in separate commands, use the `send --dry-run` artifact as the final approval copy for that send.
- The current probe result on this machine is stronger than a simple delay: the verified CLI-created probe thread existed under `.codex/sessions`, but did not appear in `session_index.jsonl` and had no row in `state_5.sqlite`. `TimelineForWindowsCodex` still found it by scanning session files.
- A later existing-session resume test on this machine showed a second mismatch pattern: the raw session JSONL and `TimelineForWindowsCodex` export contained the newest turns, while the Windows Codex UI omitted one middle user/assistant pair even though a later pair in the same session was visible.
- Practical stance for this machine: use Windows Codex UI for visual management, `TimelineForWindowsCodex` for latest transcript verification, and raw `.codex/sessions/*.jsonl` as last-resort evidence.

Send all, dry-run first:

```powershell
dock-windows-codex-sender send-all --kind bootstrap --dry-run
```

Actual send-all requires an explicit confirmation flag:

```powershell
dock-windows-codex-sender send-all --kind bootstrap --confirm-send-all
```

## Development checks

```powershell
pytest
```

## Safety rules

- Default to dry-run where possible.
- Never send to all repos without first checking the rendered prompts.
- Refuse actual `send-all` unless `--confirm-send-all` is given.
- Never delete raw input files.
- Never perform deploy, merge, external post, or secret changes.
- Keep all sent prompts in `data/sent`.
- Keep send logs in `data/logs/send-log.jsonl`.
