# Runbook

## First setup

```powershell
cd C:\apps
git clone https://github.com/amano0406/DockForWindowsCodexSender.git
cd DockForWindowsCodexSender
copy config\repos.example.yaml config\repos.yaml
.\scripts\docker.ps1 settings init
```

Edit `config/repos.yaml`.

This product has no Web UI. Operate it through the Docker wrapper commands below.
Direct host execution of `dock-windows-codex-sender` is blocked by default.
Docker Desktop must be running before using the wrapper scripts.
Codex CLI must be visible from inside the container; Windows `PATH` alone is not enough.

If Codex CLI is available only in WSL, set:

```powershell
$env:DOCK_CODEX_BIN = "wsl.exe /mnt/c/Users/amano/.codex/bin/wsl/codex"
```

Do not assume `wsl.exe codex` is enough in non-interactive runs.

Inside Docker, the sender converts a configured `wsl.exe /mnt/c/.../codex` launcher
to the mounted `/mnt/c/.../codex` path automatically.

## Render prompt

```powershell
.\scripts\docker.ps1 prompt render --repo timeline_for_chatgpt --kind bootstrap
```

Optional:

```powershell
.\scripts\docker.ps1 prompt render --repo timeline_for_chatgpt --kind bootstrap --run-id ui-probe-001
```

Check and note:

- `run_id`
- `prompt_sha256`
- `prompt_path`

## Dry-run send

```powershell
.\scripts\docker.ps1 send --repo timeline_for_chatgpt --kind bootstrap --dry-run
```

Dry-run is the approval surface for:

- target repo
- prompt path
- prompt body in `data/outbox`
- planned `codex exec` command

If you also used `prompt render` earlier, prefer the `send --dry-run` outbox file as the final approval copy for that actual send attempt.

## Send to existing session

```powershell
.\scripts\docker.ps1 send --repo timeline_for_chatgpt --kind bootstrap --resume 019dcbc7-fe5f-7ae3-8983-da7a703d9cf0 --dry-run
```

Or:

```powershell
.\scripts\docker.ps1 send --repo timeline_for_chatgpt --kind bootstrap --resume-last --dry-run
```

Notes:

- `--resume` targets a specific existing session id or thread name.
- `--resume-last` depends on Codex CLI's repo-filtered "most recent session" behavior, so use it only when the target repo has a clear latest session.
- Resume mode is intentionally not supported on `send-all`.

## Read-only verification probe

```powershell
.\scripts\docker.ps1 send --repo timeline_for_windows_codex --kind ui_sync_probe --run-id ui-probe-001 --dry-run
```

Then run the actual send only when you want to validate `.codex` / Timeline capture behavior.

## Actual send

```powershell
.\scripts\docker.ps1 send --repo timeline_for_chatgpt --kind bootstrap
```

After actual send, verify in this order:

1. Open `data/logs/send-log.jsonl` and confirm `run_id`, `prompt_sha256`, `outbox_path`, `sent_path`, `status`, and, if present, `observed_thread_id` / `observed_session_path`.
2. Open the `data/outbox` or `data/sent` prompt file and confirm the same verification metadata is embedded in the body.
3. If `observed_session_path` exists, treat it as the primary transcript evidence path even when Windows Codex UI or `session_index.jsonl` has not caught up.
4. Optionally check Windows Codex UI manually if you need visual confirmation. This is outside the product boundary and may not show the latest CLI-sent content.
5. If the task changed files, verify the actual changed files and test results in the target repo. Do not rely on UI summary text alone.

If step 3 fails, treat CLI to UI synchronization as unverified in that environment and continue using file/log evidence as the source of truth.

## Send-all dry-run

```powershell
.\scripts\docker.ps1 send-all --kind bootstrap --dry-run
```

## Send-all actual

```powershell
.\scripts\docker.ps1 send-all --kind bootstrap --confirm-send-all
```

Do not run actual send-all before inspecting rendered prompts.
