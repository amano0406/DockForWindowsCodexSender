# Runbook

## First setup

```powershell
git clone https://github.com/amano0406/DockForWindowsCodexSender.git
cd DockForWindowsCodexSender
py -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
copy config\repos.example.yaml config\repos.yaml
```

Edit `config/repos.yaml`.

If Codex CLI is available only in WSL, set:

```powershell
$env:DOCK_CODEX_BIN = "wsl.exe /mnt/c/Users/amano/.codex/bin/wsl/codex"
```

Do not assume `wsl.exe codex` is enough in non-interactive runs.

## Render prompt

```powershell
dock-windows-codex-sender prompt render --repo timeline_for_chatgpt --kind bootstrap
```

Optional:

```powershell
dock-windows-codex-sender prompt render --repo timeline_for_chatgpt --kind bootstrap --run-id ui-probe-001
```

Check and note:

- `run_id`
- `prompt_sha256`
- `prompt_path`

## Dry-run send

```powershell
dock-windows-codex-sender send --repo timeline_for_chatgpt --kind bootstrap --dry-run
```

Dry-run is the approval surface for:

- target repo
- prompt path
- prompt body in `data/outbox`
- planned `codex exec` command

If you also used `prompt render` earlier, prefer the `send --dry-run` outbox file as the final approval copy for that actual send attempt.

## Send to existing session

```powershell
dock-windows-codex-sender send --repo timeline_for_chatgpt --kind bootstrap --resume 019dcbc7-fe5f-7ae3-8983-da7a703d9cf0 --dry-run
```

Or:

```powershell
dock-windows-codex-sender send --repo timeline_for_chatgpt --kind bootstrap --resume-last --dry-run
```

Notes:

- `--resume` targets a specific existing session id or thread name.
- `--resume-last` depends on Codex CLI's repo-filtered "most recent session" behavior, so use it only when the target repo has a clear latest session.
- Resume mode is intentionally not supported on `send-all`.

## Read-only verification probe

```powershell
dock-windows-codex-sender send --repo timeline_for_windows_codex --kind ui_sync_probe --run-id ui-probe-001 --dry-run
```

Then run the actual send only when you want to validate `.codex` / Timeline capture behavior.

## Actual send

```powershell
dock-windows-codex-sender send --repo timeline_for_chatgpt --kind bootstrap
```

After actual send, verify in this order:

1. Open `data/logs/send-log.jsonl` and confirm `run_id`, `prompt_sha256`, `outbox_path`, `sent_path`, `status`, and, if present, `observed_thread_id` / `observed_session_path`.
2. Open the `data/outbox` or `data/sent` prompt file and confirm the same verification metadata is embedded in the body.
3. If `observed_session_path` exists, treat it as the primary transcript evidence path even when Windows Codex UI or `session_index.jsonl` has not caught up.
4. In Windows Codex UI, confirm the same `run_id` is visible in the prompt/thread view if the environment surfaces it.
5. If the task changed files, verify the actual changed files and test results in the target repo. Do not rely on UI summary text alone.

If step 3 fails, treat CLI to UI synchronization as unverified in that environment and continue using file/log evidence as the source of truth.

## Send-all dry-run

```powershell
dock-windows-codex-sender send-all --kind bootstrap --dry-run
```

## Send-all actual

```powershell
dock-windows-codex-sender send-all --kind bootstrap --confirm-send-all
```

Do not run actual send-all before inspecting rendered prompts.
