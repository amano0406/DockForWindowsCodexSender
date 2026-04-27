from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .models import SendResult


def now_stamp() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y%m%d-%H%M%S-%f")


def ensure_data_dirs(data_root: Path) -> None:
    for name in ["outbox", "sent", "logs", "state"]:
        (data_root / name).mkdir(parents=True, exist_ok=True)


def write_prompt_file(
    *,
    data_root: Path,
    bucket: str,
    run_id: str,
    repo_id: str,
    kind: str,
    content: str,
) -> Path:
    ensure_data_dirs(data_root)
    stamp = now_stamp()
    safe_run_id = run_id.replace("/", "-").replace("\\", "-").replace(" ", "_")
    path = data_root / bucket / f"{stamp}-{safe_run_id}-{repo_id}-{kind}.md"
    path.write_text(content, encoding="utf-8")
    return path


def append_send_log(*, data_root: Path, result: SendResult) -> None:
    ensure_data_dirs(data_root)
    log_path = data_root / "logs" / "send-log.jsonl"
    record = {
        "repo_id": result.repo_id,
        "kind": result.kind,
        "run_id": result.run_id,
        "prompt_sha256": result.prompt_sha256,
        "outbox_path": str(result.outbox_path),
        "sent_path": str(result.sent_path) if result.sent_path else None,
        "observed_thread_id": result.observed_thread_id,
        "observed_session_path": (
            str(result.observed_session_path)
            if result.observed_session_path
            else None
        ),
        "transport": result.transport,
        "dry_run": result.dry_run,
        "status": result.status,
        "command": result.command,
        "returncode": result.returncode,
        "error": result.error,
        "logged_at": datetime.now(timezone.utc).astimezone().isoformat(),
    }
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
