# DockForWindowsCodexSender

Send-only bridge for local Windows Codex operations.

This project starts small on purpose:

- Generate Codex prompts from templates.
- Render prompts per target repository.
- Dry-run before sending.
- Send prompts through Codex CLI when explicitly requested.
- Save rendered prompts, sent prompts, and send logs.
- Provide no first-party Web UI, dashboard, browser UI, or local web service.
- Treat Windows Codex UI as an external manual observation surface, not part of this product.
- Do **not** read or analyze Codex responses yet.
- Do **not** automate the Windows Codex app UI.

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

## CLI-only product boundary

This repository is intentionally CLI-only.

It should not contain or add:

- first-party Web UI or dashboard code
- browser frontend code
- localhost service hosts
- Docker Compose web stacks
- Windows Codex app UI automation

The Windows Codex app can still be checked manually by a human. That manual check is outside this product boundary and is not the source of truth for sent content.

## Transport boundary

- CLI send is the primary path for automation and log preservation.
- Windows Codex UI can be useful for human visual/thread management, but this tool does not implement or control it.
- CLI send to app UI synchronization is not guaranteed in v0.1 and should be treated as a verification target, not an assumption.
- Receive-side organization is a later step using `send-log.jsonl`, transcript exports, and `TimelineForWindowsCodex`.
- Windows app UI automation is out of scope for this product.

## Docker-first execution

Normal operation is Docker-only. Direct host execution of `dock-windows-codex-sender`
is blocked by default so local Python, PATH, and shell differences do not become part
of the runtime contract.

Entry-point policy:

- Front door: Windows PowerShell, using `scripts\docker.ps1` and `scripts\docker-test.ps1`.
- Back door: WSL/bash, using `scripts/docker-wsl.sh` and `scripts/docker-test-wsl.sh` only when PowerShell is not practical, for example from a WSL-based Codex automation context.
- Blocked path: direct host CLI execution without Docker.

Required host-side prerequisites:

- Windows with Docker Desktop running.
- PowerShell for `scripts\docker.ps1` and `scripts\docker-test.ps1`.
- This repository under `C:\apps\DockForWindowsCodexSender`, with target repos as siblings under `C:\apps`.
- Codex CLI available from inside the container. On this machine the expected mounted binary is `/mnt/c/Users/amano/.codex/bin/wsl/codex`.

Not required for normal operation:

- Host Python virtualenv.
- Host-side `pip install -e`.
- Direct host execution of `dock-windows-codex-sender`.

Use the Docker wrapper from the repository root:

```powershell
.\scripts\docker.ps1 doctor
```

The wrapper builds `dock-for-windows-codex-sender:local`, mounts `C:\apps` and the
local Codex home, then runs the CLI inside the container. If no arguments are passed,
it runs `doctor`.

After a successful build, add `-SkipBuild` when you intentionally want a faster repeat run:

```powershell
.\scripts\docker.ps1 -SkipBuild repos list
```

For unit tests, use:

```powershell
.\scripts\docker-test.ps1
```

WSL back-door equivalents are available but are not the normal user-facing route:

```bash
./scripts/docker-wsl.sh doctor
./scripts/docker-test-wsl.sh
```

Host execution is allowed only for explicit test/debug exceptions:

```powershell
$env:DOCK_CODEX_ALLOW_HOST_CLI = "1"
pytest
```

Do not use `DOCK_CODEX_ALLOW_HOST_CLI` for normal sends.

## Configure repositories

Initialize local settings once:

```powershell
.\scripts\docker.ps1 settings init
```

This creates `settings.json` only when it does not already exist. `settings.example.json` is tracked by Git; `settings.json` is local-only and ignored by Git.

```powershell
copy config\repos.example.yaml config\repos.yaml
```

Edit `config/repos.yaml` and set local repository paths.

If `config/repos.yaml` does not exist, the CLI falls back to `config/repos.example.yaml`.

## Prompt/config files

- `settings.example.json`: tracked example for local CLI settings
- `settings.json`: local-only settings, created by `settings init`
- `config/repos.yaml`: local repo registry
- `config/repos.example.yaml`: example repo registry and fallback
- `config/prompts.yaml`: prompt kind/profile mapping
- `prompts/kinds/*.md`: per-command templates
- `prompts/common/*.md`: shared context fragments
- `prompts/products/*.md`: product-specific notes

## Fixed local data policy

This Dock product uses fixed local paths by default:

```text
data/
  outbox/
  sent/
  logs/
  state/
```

- `data/outbox/`: every rendered send attempt
- `data/sent/`: copies of prompts after successful actual sends
- `data/logs/send-log.jsonl`: append-only send evidence
- `data/state/`: reserved local sender state

`DOCK_CODEX_DATA_ROOT` may relocate the whole data root. Arbitrary per-command input/output paths are intentionally not the normal workflow.

This repository does not own Timeline `Job` / `Run` execution output. For this sender, the stable evidence unit is a rendered prompt plus send attempt identified by `run_id`, `prompt_sha256`, and the JSONL send log record. Target Timeline repositories remain responsible for their own `Job` / `Run` / `Artifact` contracts.

## Codex binary setup

Docker-first operation requires a Codex CLI binary that is visible inside the container.
Windows `PATH` is not the runtime contract for this product.

If Codex CLI exists only inside WSL, `settings init` stores the auto-detected launcher in `settings.json` when possible. The CLI can also auto-detect this known local launcher:

```text
wsl.exe /mnt/c/Users/amano/.codex/bin/wsl/codex
```

Inside Docker, the sender strips the outer `wsl.exe` launcher and uses the mounted
Codex binary path directly:

```text
/mnt/c/Users/amano/.codex/bin/wsl/codex
```

If auto-detection does not work, pass a launcher command string such as:

```powershell
$env:DOCK_CODEX_BIN = "wsl.exe /mnt/c/Users/amano/.codex/bin/wsl/codex"
```

`wsl.exe codex` alone may fail in non-interactive runs because the WSL shell `PATH` is not guaranteed to include `codex`.

## Basic commands

List configured repositories:

```powershell
.\scripts\docker.ps1 repos list
```

Check whether local settings are ready for actual send:

```powershell
.\scripts\docker.ps1 doctor
```

If Codex CLI exists only inside WSL and auto-detection does not find it:

```powershell
.\scripts\docker.ps1 doctor --codex-bin "wsl.exe /mnt/c/Users/amano/.codex/bin/wsl/codex"
```

`doctor` is read-only. It checks repository config, prompt config, data directories, Codex CLI launchability, CLI-only boundaries, and whether `AGENTS.md` has reappeared.

Render one prompt:

```powershell
.\scripts\docker.ps1 prompt render --repo timeline_for_chatgpt --kind bootstrap
```

If you want a human-chosen verification token, add `--run-id <token>`.

Render all bootstrap prompts to `data/outbox`:

```powershell
.\scripts\docker.ps1 prompt render-all --kind bootstrap
```

Dry-run send:

```powershell
.\scripts\docker.ps1 send --repo timeline_for_chatgpt --kind bootstrap --dry-run
```

Send into an existing Codex session:

```powershell
.\scripts\docker.ps1 send --repo timeline_for_chatgpt --kind bootstrap --resume 019dcbc7-fe5f-7ae3-8983-da7a703d9cf0
```

Resume the most recent session filtered by the target repo working directory:

```powershell
.\scripts\docker.ps1 send --repo timeline_for_chatgpt --kind bootstrap --resume-last
```

Read-only verification probe:

```powershell
.\scripts\docker.ps1 send --repo timeline_for_windows_codex --kind ui_sync_probe --run-id ui-probe-001 --dry-run
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
.\scripts\docker.ps1 send --repo timeline_for_chatgpt --kind bootstrap
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
.\scripts\docker.ps1 send-all --kind bootstrap --dry-run
```

Actual send-all requires an explicit confirmation flag:

```powershell
.\scripts\docker.ps1 send-all --kind bootstrap --confirm-send-all
```

## Development checks

```powershell
.\scripts\docker-test.ps1
```

## Safety rules

- Default to dry-run where possible.
- Never send to all repos without first checking the rendered prompts.
- Refuse actual `send-all` unless `--confirm-send-all` is given.
- Never delete raw input files.
- Never perform deploy, merge, external post, or secret changes.
- Keep all sent prompts in `data/sent`.
- Keep send logs in `data/logs/send-log.jsonl`.
- Run normal CLI operations through `scripts\docker.ps1`; host CLI is test-only and requires `DOCK_CODEX_ALLOW_HOST_CLI=1`.
