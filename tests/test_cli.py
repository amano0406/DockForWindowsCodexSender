import argparse
import json
from pathlib import Path

import pytest

from dock_for_windows_codex_sender import cli
from dock_for_windows_codex_sender.models import SendResult


def make_test_project(root: Path) -> None:
    (root / "config").mkdir(parents=True, exist_ok=True)
    (root / "prompts" / "common").mkdir(parents=True, exist_ok=True)
    (root / "prompts" / "kinds").mkdir(parents=True, exist_ok=True)
    (root / "prompts" / "products").mkdir(parents=True, exist_ok=True)
    (root / "targets" / "timeline_for_chatgpt").mkdir(parents=True, exist_ok=True)

    (root / "config" / "repos.example.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "",
                "repos:",
                "  timeline_for_chatgpt:",
                "    name: TimelineForChatGPT",
                "    path: targets/timeline_for_chatgpt",
                "    product_family: timeline",
                "    priority: high",
                "    prompt_profile: timeline_chatgpt",
                "    enabled: true",
            ]
        ),
        encoding="utf-8",
    )
    (root / "config" / "prompts.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "",
                "kinds:",
                "  bootstrap:",
                "    template: prompts/kinds/bootstrap.md",
                "",
                "common_context:",
                "  operating_note: prompts/common/operating_note.md",
                "  send_verification_block: prompts/common/send_verification_block.md",
                "",
                "profiles:",
                "  timeline_chatgpt:",
                "    product_note: prompts/products/timeline_for_chatgpt.md",
            ]
        ),
        encoding="utf-8",
    )
    (root / "prompts" / "common" / "operating_note.md").write_text(
        "Common operating note.",
        encoding="utf-8",
    )
    (root / "prompts" / "common" / "send_verification_block.md").write_text(
        "\n".join(
            [
                "Run ID: {{ meta.run_id }}",
                "Rendered at: {{ meta.rendered_at }}",
            ]
        ),
        encoding="utf-8",
    )
    (root / "prompts" / "products" / "timeline_for_chatgpt.md").write_text(
        "Product specific note.",
        encoding="utf-8",
    )
    (root / "prompts" / "kinds" / "bootstrap.md").write_text(
        "\n".join(
            [
                "# Bootstrap",
                "Repo: {{ repo.name }}",
                "Path: {{ repo.path }}",
                "{{ common.send_verification_block }}",
                "{{ common.operating_note }}",
                "{{ product_note }}",
            ]
        ),
        encoding="utf-8",
    )


def make_send_args(root: Path, *, dry_run: bool) -> argparse.Namespace:
    return argparse.Namespace(
        repos_config=root / "config" / "repos.yaml",
        prompts_config=root / "config" / "prompts.yaml",
        data_root=root / "data",
        repo="timeline_for_chatgpt",
        kind="bootstrap",
        dry_run=dry_run,
        codex_bin="codex",
        resume=None,
        resume_last=False,
        run_id=None,
    )


def read_send_log(root: Path) -> dict[str, object]:
    lines = (root / "data" / "logs" / "send-log.jsonl").read_text(encoding="utf-8").splitlines()
    return json.loads(lines[-1])


def test_cmd_send_dry_run_uses_example_config_and_logs(tmp_path: Path, monkeypatch, capsys):
    make_test_project(tmp_path)
    monkeypatch.setattr(cli, "PROJECT_ROOT", tmp_path)

    rc = cli.cmd_send(make_send_args(tmp_path, dry_run=True))

    assert rc == 0
    outbox_files = list((tmp_path / "data" / "outbox").glob("*.md"))
    sent_files = list((tmp_path / "data" / "sent").glob("*.md"))
    assert len(outbox_files) == 1
    assert sent_files == []

    log_record = read_send_log(tmp_path)
    assert log_record["status"] == "dry-run"
    assert log_record["run_id"].startswith("run-")
    assert log_record["prompt_sha256"]
    assert log_record["sent_path"] is None
    assert log_record["outbox_path"] == str(outbox_files[0])

    captured = capsys.readouterr().out
    assert "run_id=run-" in captured
    assert "prompt_sha256=" in captured
    assert "status=dry-run" in captured
    assert f"outbox_path={outbox_files[0]}" in captured


def test_cmd_send_actual_success_writes_sent_copy(tmp_path: Path, monkeypatch):
    make_test_project(tmp_path)
    monkeypatch.setattr(cli, "PROJECT_ROOT", tmp_path)

    def fake_send_via_codex_cli(**kwargs) -> SendResult:
        repo = kwargs["repo"]
        return SendResult(
            repo_id=repo.repo_id,
            kind=kwargs["kind"],
            run_id=kwargs["run_id"],
            prompt_sha256=kwargs["prompt_sha256"],
            outbox_path=kwargs["outbox_path"],
            sent_path=None,
            observed_thread_id="019dcbc7-fe5f-7ae3-8983-da7a703d9cf0",
            observed_session_path=Path("/tmp/fake-session.jsonl"),
            transport="codex-cli",
            dry_run=False,
            status="sent",
            command=["codex", "exec", "-"],
            returncode=0,
        )

    monkeypatch.setattr(cli, "send_via_codex_cli", fake_send_via_codex_cli)

    rc = cli.cmd_send(make_send_args(tmp_path, dry_run=False))

    assert rc == 0
    outbox_files = list((tmp_path / "data" / "outbox").glob("*.md"))
    sent_files = list((tmp_path / "data" / "sent").glob("*.md"))
    assert len(outbox_files) == 1
    assert len(sent_files) == 1
    assert sent_files[0].read_text(encoding="utf-8") == outbox_files[0].read_text(encoding="utf-8")

    log_record = read_send_log(tmp_path)
    assert log_record["status"] == "sent"
    assert log_record["run_id"].startswith("run-")
    assert log_record["sent_path"] == str(sent_files[0])
    assert log_record["observed_thread_id"] == "019dcbc7-fe5f-7ae3-8983-da7a703d9cf0"
    assert log_record["observed_session_path"] == str(Path("/tmp/fake-session.jsonl"))


def test_cmd_send_failure_keeps_only_outbox_and_logs_error(tmp_path: Path, monkeypatch):
    make_test_project(tmp_path)
    monkeypatch.setattr(cli, "PROJECT_ROOT", tmp_path)

    def fake_send_via_codex_cli(**kwargs) -> SendResult:
        repo = kwargs["repo"]
        return SendResult(
            repo_id=repo.repo_id,
            kind=kwargs["kind"],
            run_id=kwargs["run_id"],
            prompt_sha256=kwargs["prompt_sha256"],
            outbox_path=kwargs["outbox_path"],
            sent_path=None,
            observed_thread_id=None,
            observed_session_path=None,
            transport="codex-cli",
            dry_run=False,
            status="failed",
            command=["codex", "exec", "-"],
            returncode=23,
            error="Codex CLI exited with 23.",
        )

    monkeypatch.setattr(cli, "send_via_codex_cli", fake_send_via_codex_cli)

    rc = cli.cmd_send(make_send_args(tmp_path, dry_run=False))

    assert rc == 1
    assert len(list((tmp_path / "data" / "outbox").glob("*.md"))) == 1
    assert list((tmp_path / "data" / "sent").glob("*.md")) == []

    log_record = read_send_log(tmp_path)
    assert log_record["status"] == "failed"
    assert log_record["sent_path"] is None
    assert log_record["error"] == "Codex CLI exited with 23."


def test_cmd_send_dry_run_resume_prints_resume_command(tmp_path: Path, monkeypatch, capsys):
    make_test_project(tmp_path)
    monkeypatch.setattr(cli, "PROJECT_ROOT", tmp_path)
    args = make_send_args(tmp_path, dry_run=True)
    args.resume = "existing-session"

    rc = cli.cmd_send(args)

    assert rc == 0
    captured = capsys.readouterr().out
    assert "status=dry-run" in captured
    assert "command=codex exec resume existing-session -" in captured


def test_cmd_send_all_requires_confirm_for_actual_send(tmp_path: Path):
    args = argparse.Namespace(
        repos_config=tmp_path / "config" / "repos.yaml",
        prompts_config=tmp_path / "config" / "prompts.yaml",
        data_root=tmp_path / "data",
        kind="bootstrap",
        dry_run=False,
        confirm_send_all=False,
        codex_bin="codex",
        run_id=None,
    )

    with pytest.raises(SystemExit, match="--confirm-send-all"):
        cli.cmd_send_all(args)
