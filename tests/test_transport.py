import subprocess
from pathlib import Path

import pytest

from dock_for_windows_codex_sender.models import RepoConfig
from dock_for_windows_codex_sender.transport import (
    build_codex_exec_command,
    build_codex_resume_command,
    default_codex_bin,
    detect_observed_session,
    extract_thread_id_from_session_path,
    is_wsl_command,
    parse_command_prefix,
    send_via_codex_cli,
    snapshot_session_files,
    to_wsl_path,
)


def test_build_codex_exec_command():
    repo_path = Path("/tmp/example")
    command = build_codex_exec_command("codex", repo_path)
    assert command == ["codex", "exec", "--cd", str(repo_path), "-"]


def test_build_codex_resume_command_for_explicit_session():
    command = build_codex_resume_command("codex", session_id_or_name="019dcbc7-fe5f-7ae3-8983-da7a703d9cf0")
    assert command == [
        "codex",
        "exec",
        "resume",
        "019dcbc7-fe5f-7ae3-8983-da7a703d9cf0",
        "-",
    ]


def test_build_codex_resume_command_for_last_session():
    command = build_codex_resume_command("codex", resume_last=True)
    assert command == ["codex", "exec", "resume", "--last", "-"]


def test_parse_command_prefix_and_detect_wsl():
    prefix = parse_command_prefix("wsl.exe codex")
    assert prefix == ["wsl.exe", "codex"]
    assert is_wsl_command(prefix) is True


def test_to_wsl_path_from_windows_style_path():
    assert to_wsl_path(Path(r"C:\apps\TimelineForWindowsCodex")) == "/mnt/c/apps/TimelineForWindowsCodex"


def test_build_codex_exec_command_for_wsl_launcher():
    repo_path = Path(r"C:\apps\TimelineForWindowsCodex")
    command = build_codex_exec_command("wsl.exe codex", repo_path)
    assert command == [
        "wsl.exe",
        "codex",
        "exec",
        "--cd",
        "/mnt/c/apps/TimelineForWindowsCodex",
        "-",
    ]


def test_default_codex_bin_prefers_env_override(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DOCK_CODEX_BIN", "custom-codex")

    assert default_codex_bin() == "custom-codex"


def test_default_codex_bin_prefers_explicit_config(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DOCK_CODEX_BIN", "env-codex")

    assert default_codex_bin("settings-codex") == "settings-codex"


def test_default_codex_bin_uses_wsl_candidate_when_codex_is_not_on_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    candidate = tmp_path / "codex"
    candidate.write_text("", encoding="utf-8")

    def fake_which(command: str) -> str | None:
        return "wsl.exe" if command == "wsl.exe" else None

    monkeypatch.delenv("DOCK_CODEX_BIN", raising=False)
    monkeypatch.delenv("USERPROFILE", raising=False)
    monkeypatch.delenv("USERNAME", raising=False)
    monkeypatch.setattr("dock_for_windows_codex_sender.transport.shutil.which", fake_which)
    monkeypatch.setattr(
        "dock_for_windows_codex_sender.transport.candidate_wsl_codex_commands",
        lambda: iter([(candidate.as_posix(), candidate)]),
    )

    assert default_codex_bin() == f"wsl.exe {candidate.as_posix()}"


def test_send_via_codex_cli_returns_failed_result_when_binary_missing(tmp_path: Path):
    repo = RepoConfig(
        repo_id="example",
        name="Example",
        path=tmp_path,
        product_family="dock",
        priority="high",
        prompt_profile="example",
    )

    result = send_via_codex_cli(
        repo=repo,
        kind="bootstrap",
        run_id="run-test-001",
        prompt_sha256="abc123",
        outbox_path=tmp_path / "prompt.md",
        prompt_text="hello",
        codex_bin="definitely-missing-codex-bin",
        dry_run=False,
    )

    assert result.status == "failed"
    assert result.run_id == "run-test-001"
    assert result.prompt_sha256 == "abc123"
    assert result.sent_path is None
    assert result.observed_thread_id is None
    assert result.observed_session_path is None
    assert result.error is not None


def test_extract_thread_id_from_session_path_uses_filename(tmp_path: Path):
    session_path = tmp_path / "rollout-2026-04-27T06-52-54-019dcbc7-fe5f-7ae3-8983-da7a703d9cf0.jsonl"
    session_path.write_text("{}", encoding="utf-8")
    assert extract_thread_id_from_session_path(session_path) == "019dcbc7-fe5f-7ae3-8983-da7a703d9cf0"


def test_detect_observed_session_prefers_run_id_match(tmp_path: Path):
    codex_home = tmp_path / ".codex"
    sessions_root = codex_home / "sessions" / "2026" / "04" / "27"
    sessions_root.mkdir(parents=True, exist_ok=True)

    before_snapshot = snapshot_session_files(codex_home)

    other_session = sessions_root / "rollout-2026-04-27T06-52-54-019dcbc7-fe5f-7ae3-8983-da7a703d9cf1.jsonl"
    other_session.write_text("no matching run id", encoding="utf-8")
    matched_session = sessions_root / "rollout-2026-04-27T06-52-54-019dcbc7-fe5f-7ae3-8983-da7a703d9cf0.jsonl"
    matched_session.write_text("Run ID: ui-sync-probe-001", encoding="utf-8")

    observed_thread_id, observed_session_path = detect_observed_session(
        codex_home=codex_home,
        before_snapshot=before_snapshot,
        run_id="ui-sync-probe-001",
    )

    assert observed_thread_id == "019dcbc7-fe5f-7ae3-8983-da7a703d9cf0"
    assert observed_session_path == matched_session.resolve()


def test_send_via_codex_cli_observes_session_file_after_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    repo = RepoConfig(
        repo_id="example",
        name="Example",
        path=tmp_path / "repo",
        product_family="dock",
        priority="high",
        prompt_profile="example",
    )
    repo.path.mkdir(parents=True, exist_ok=True)
    codex_home = tmp_path / ".codex"
    sessions_root = codex_home / "sessions" / "2026" / "04" / "27"
    sessions_root.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr("dock_for_windows_codex_sender.transport.shutil.which", lambda _: "codex")

    def fake_run(*args, **kwargs):
        session_path = sessions_root / "rollout-2026-04-27T06-52-54-019dcbc7-fe5f-7ae3-8983-da7a703d9cf0.jsonl"
        session_path.write_text("Run ID: run-test-001", encoding="utf-8")
        return subprocess.CompletedProcess(args=args[0], returncode=0)

    monkeypatch.setattr("dock_for_windows_codex_sender.transport.subprocess.run", fake_run)

    result = send_via_codex_cli(
        repo=repo,
        kind="bootstrap",
        run_id="run-test-001",
        prompt_sha256="abc123",
        outbox_path=tmp_path / "prompt.md",
        prompt_text="hello",
        codex_bin="codex",
        codex_home=codex_home,
        dry_run=False,
    )

    assert result.status == "sent"
    assert result.observed_thread_id == "019dcbc7-fe5f-7ae3-8983-da7a703d9cf0"
    assert result.observed_session_path == (
        sessions_root / "rollout-2026-04-27T06-52-54-019dcbc7-fe5f-7ae3-8983-da7a703d9cf0.jsonl"
    ).resolve()


def test_send_via_codex_cli_resume_uses_repo_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    repo = RepoConfig(
        repo_id="example",
        name="Example",
        path=tmp_path / "repo",
        product_family="dock",
        priority="high",
        prompt_profile="example",
    )
    repo.path.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr("dock_for_windows_codex_sender.transport.shutil.which", lambda _: "codex")
    captured: dict[str, object] = {}

    def fake_run(*args, **kwargs):
        captured["command"] = args[0]
        captured["cwd"] = kwargs.get("cwd")
        return subprocess.CompletedProcess(args=args[0], returncode=0)

    monkeypatch.setattr("dock_for_windows_codex_sender.transport.subprocess.run", fake_run)

    result = send_via_codex_cli(
        repo=repo,
        kind="bootstrap",
        run_id="run-test-001",
        prompt_sha256="abc123",
        outbox_path=tmp_path / "prompt.md",
        prompt_text="hello",
        codex_bin="codex",
        resume_session="existing-session",
        dry_run=False,
    )

    assert result.status == "sent"
    assert captured["command"] == ["codex", "exec", "resume", "existing-session", "-"]
    assert captured["cwd"] == repo.path
