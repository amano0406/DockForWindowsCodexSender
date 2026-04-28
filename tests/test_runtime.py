from __future__ import annotations

import pytest

from dock_for_windows_codex_sender import runtime


def test_docker_hint_env_alone_is_not_trusted(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv(runtime.IN_DOCKER_ENV, "1")
    monkeypatch.setattr(runtime, "docker_env_file_exists", lambda: False)
    monkeypatch.setattr(runtime, "read_cgroup_text", lambda: "")

    assert runtime.is_docker_runtime() is False


def test_enforce_cli_runtime_blocks_host_without_explicit_allow(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.delenv(runtime.ALLOW_HOST_CLI_ENV, raising=False)
    monkeypatch.delenv(runtime.IN_DOCKER_ENV, raising=False)
    monkeypatch.setattr(runtime, "is_docker_runtime", lambda: False)

    with pytest.raises(SystemExit, match="Host CLI execution is blocked"):
        runtime.enforce_cli_runtime()


def test_enforce_cli_runtime_allows_explicit_test_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv(runtime.ALLOW_HOST_CLI_ENV, "1")
    monkeypatch.setattr(runtime, "is_docker_runtime", lambda: False)

    runtime.enforce_cli_runtime()


def test_enforce_cli_runtime_allows_docker(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv(runtime.ALLOW_HOST_CLI_ENV, raising=False)
    monkeypatch.setattr(runtime, "is_docker_runtime", lambda: True)

    runtime.enforce_cli_runtime()
