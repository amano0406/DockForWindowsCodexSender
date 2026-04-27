from __future__ import annotations

import os
import re
import shlex
import shutil
import subprocess
from pathlib import Path

from .models import RepoConfig, SendResult

_THREAD_ID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)


def parse_command_prefix(command: str) -> list[str]:
    tokens = shlex.split(command, posix=False)
    if not tokens:
        raise ValueError("Codex command must not be empty.")
    return tokens


def is_wsl_command(command_prefix: list[str]) -> bool:
    launcher = Path(command_prefix[0]).name.lower()
    return launcher in {"wsl", "wsl.exe"}


def to_wsl_path(path: Path) -> str:
    value = str(path)
    if len(value) >= 3 and value[1:3] == ":\\":
        drive = value[0].lower()
        rest = value[3:].replace("\\", "/")
        return f"/mnt/{drive}/{rest}"
    return value.replace("\\", "/")


def build_codex_exec_command(codex_bin: str, repo_path: Path) -> list[str]:
    command_prefix = parse_command_prefix(codex_bin)
    repo_arg = to_wsl_path(repo_path) if is_wsl_command(command_prefix) else str(repo_path)
    return [*command_prefix, "exec", "--cd", repo_arg, "-"]


def build_codex_resume_command(
    codex_bin: str,
    *,
    session_id_or_name: str | None = None,
    resume_last: bool = False,
) -> list[str]:
    if session_id_or_name and resume_last:
        raise ValueError("Resume target and resume-last cannot be used together.")
    if not session_id_or_name and not resume_last:
        raise ValueError("Resume command requires a session target or resume-last.")

    command_prefix = parse_command_prefix(codex_bin)
    command = [*command_prefix, "exec", "resume"]
    if resume_last:
        command.append("--last")
    elif session_id_or_name:
        command.append(session_id_or_name)
    command.append("-")
    return command


def default_codex_home() -> Path:
    return Path(os.getenv("DOCK_CODEX_HOME", Path.home() / ".codex"))


def snapshot_session_files(codex_home: Path) -> dict[Path, int]:
    sessions_root = codex_home / "sessions"
    if not sessions_root.exists():
        return {}

    snapshot: dict[Path, int] = {}
    for session_path in sessions_root.rglob("*.jsonl"):
        try:
            snapshot[session_path.resolve()] = session_path.stat().st_mtime_ns
        except OSError:
            continue
    return snapshot


def session_contains_token(session_path: Path, token: str) -> bool:
    if not token:
        return False

    try:
        return token in session_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False


def extract_thread_id_from_session_path(session_path: Path) -> str | None:
    filename_match = _THREAD_ID_RE.search(session_path.name)
    if filename_match:
        return filename_match.group(0)

    try:
        with session_path.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                line_match = _THREAD_ID_RE.search(line)
                if line_match:
                    return line_match.group(0)
    except OSError:
        return None

    return None


def detect_observed_session(
    *,
    codex_home: Path,
    before_snapshot: dict[Path, int],
    run_id: str,
) -> tuple[str | None, Path | None]:
    after_snapshot = snapshot_session_files(codex_home)
    candidates = [
        path
        for path, mtime in after_snapshot.items()
        if path not in before_snapshot or mtime > before_snapshot[path]
    ]
    if not candidates:
        return None, None

    matching_candidates = [path for path in candidates if session_contains_token(path, run_id)]
    selected = matching_candidates or candidates
    session_path = max(
        selected,
        key=lambda path: (after_snapshot.get(path, 0), str(path)),
    )
    return extract_thread_id_from_session_path(session_path), session_path


def send_via_codex_cli(
    *,
    repo: RepoConfig,
    kind: str,
    run_id: str,
    prompt_sha256: str,
    outbox_path: Path,
    prompt_text: str,
    codex_bin: str = "codex",
    codex_home: Path | None = None,
    resume_session: str | None = None,
    resume_last: bool = False,
    dry_run: bool = False,
) -> SendResult:
    if resume_session or resume_last:
        command = build_codex_resume_command(
            codex_bin,
            session_id_or_name=resume_session,
            resume_last=resume_last,
        )
    else:
        command = build_codex_exec_command(codex_bin, repo.path)
    command_prefix = parse_command_prefix(codex_bin)
    resolved_codex_home = codex_home or default_codex_home()

    if dry_run:
        return SendResult(
            repo_id=repo.repo_id,
            kind=kind,
            run_id=run_id,
            prompt_sha256=prompt_sha256,
            outbox_path=outbox_path,
            sent_path=None,
            observed_thread_id=None,
            observed_session_path=None,
            transport="codex-cli",
            dry_run=True,
            status="dry-run",
            command=command,
        )

    if shutil.which(command_prefix[0]) is None:
        return SendResult(
            repo_id=repo.repo_id,
            kind=kind,
            run_id=run_id,
            prompt_sha256=prompt_sha256,
            outbox_path=outbox_path,
            sent_path=None,
            observed_thread_id=None,
            observed_session_path=None,
            transport="codex-cli",
            dry_run=False,
            status="failed",
            command=command,
            error=(
                f"Codex binary not found: {codex_bin}. "
                "Install Codex CLI or set DOCK_CODEX_BIN / --codex-bin."
            ),
        )

    before_snapshot = snapshot_session_files(resolved_codex_home)

    try:
        completed = subprocess.run(
            command,
            input=prompt_text,
            text=True,
            encoding="utf-8",
            cwd=repo.path if (resume_session or resume_last) else None,
            check=False,
        )
    except OSError as exc:
        return SendResult(
            repo_id=repo.repo_id,
            kind=kind,
            run_id=run_id,
            prompt_sha256=prompt_sha256,
            outbox_path=outbox_path,
            sent_path=None,
            observed_thread_id=None,
            observed_session_path=None,
            transport="codex-cli",
            dry_run=False,
            status="failed",
            command=command,
            error=str(exc),
        )

    observed_thread_id, observed_session_path = detect_observed_session(
        codex_home=resolved_codex_home,
        before_snapshot=before_snapshot,
        run_id=run_id,
    )

    return SendResult(
        repo_id=repo.repo_id,
        kind=kind,
        run_id=run_id,
        prompt_sha256=prompt_sha256,
        outbox_path=outbox_path,
        sent_path=None,
        observed_thread_id=observed_thread_id,
        observed_session_path=observed_session_path,
        transport="codex-cli",
        dry_run=False,
        status="sent" if completed.returncode == 0 else "failed",
        command=command,
        returncode=completed.returncode,
        error=(
            None
            if completed.returncode == 0
            else f"Codex CLI exited with {completed.returncode}."
        ),
    )
