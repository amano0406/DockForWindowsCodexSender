from __future__ import annotations

import os
from pathlib import Path


ALLOW_HOST_CLI_ENV = "DOCK_CODEX_ALLOW_HOST_CLI"
IN_DOCKER_ENV = "DOCK_CODEX_IN_DOCKER"


def is_truthy(value: str | None) -> bool:
    return value is not None and value.strip().lower() in {"1", "true", "yes", "on"}


def docker_env_file_exists() -> bool:
    return Path("/.dockerenv").exists()


def read_cgroup_text() -> str:
    try:
        return Path("/proc/1/cgroup").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def is_docker_runtime() -> bool:
    # Do not trust DOCK_CODEX_IN_DOCKER by itself; a host shell can set it.
    if docker_env_file_exists():
        return True

    cgroup = read_cgroup_text()
    return any(marker in cgroup for marker in ["docker", "containerd", "kubepods"])


def is_host_cli_allowed() -> bool:
    return is_truthy(os.getenv(ALLOW_HOST_CLI_ENV))


def enforce_cli_runtime() -> None:
    if is_docker_runtime() or is_host_cli_allowed():
        return

    raise SystemExit(
        "Host CLI execution is blocked. Run through Docker, for example: "
        "powershell -ExecutionPolicy Bypass -File scripts\\docker.ps1 doctor. "
        f"For tests only, set {ALLOW_HOST_CLI_ENV}=1."
    )
