from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import load_prompts, load_repos, resolve_config_path
from .render import resolve_project_path
from .settings import settings_example_path, settings_path
from .transport import parse_command_prefix


@dataclass(frozen=True)
class DoctorCheck:
    status: str
    name: str
    message: str
    action: str | None = None


DATA_DIRS = ["outbox", "sent", "logs", "state"]
FORBIDDEN_WEB_ARTIFACTS = [
    "web",
    "frontend",
    "ui",
    "app",
    "docker-compose.yml",
    "docker-compose.yaml",
    "start.bat",
]


def ok(name: str, message: str) -> DoctorCheck:
    return DoctorCheck(status="OK", name=name, message=message)


def warn(name: str, message: str, action: str | None = None) -> DoctorCheck:
    return DoctorCheck(status="WARN", name=name, message=message, action=action)


def ng(name: str, message: str, action: str | None = None) -> DoctorCheck:
    return DoctorCheck(status="NG", name=name, message=message, action=action)


def check_repos_config(repos_config: Path) -> tuple[list[DoctorCheck], dict[str, Any]]:
    checks: list[DoctorCheck] = []
    context: dict[str, Any] = {}

    try:
        resolved_path = resolve_config_path(repos_config, example_name="repos.example.yaml")
        repos = load_repos(repos_config)
    except Exception as exc:
        checks.append(
            ng(
                "repos-config",
                f"failed to load: {exc}",
                "Check --repos-config or create config/repos.yaml from config/repos.example.yaml.",
            )
        )
        return checks, context

    enabled = [repo for repo in repos.values() if repo.enabled]
    missing_paths = [f"{repo.repo_id}={repo.path}" for repo in enabled if not repo.path.exists()]
    checks.append(ok("repos-config", f"loaded {len(repos)} repos from {resolved_path}"))
    if missing_paths:
        checks.append(
            ng(
                "repo-paths",
                "missing enabled repo paths: " + ", ".join(missing_paths),
                "Fix config/repos.yaml or disable repos that are not present locally.",
            )
        )
    else:
        checks.append(ok("repo-paths", f"all {len(enabled)} enabled repo paths exist"))

    context["repos"] = repos
    return checks, context


def check_prompts_config(prompts_config: Path, project_root: Path) -> list[DoctorCheck]:
    checks: list[DoctorCheck] = []

    try:
        resolved_path = resolve_config_path(prompts_config, example_name="prompts.example.yaml")
        config = load_prompts(prompts_config)
    except Exception as exc:
        return [
            ng(
                "prompts-config",
                f"failed to load: {exc}",
                "Check --prompts-config and config/prompts.yaml.",
            )
        ]

    missing: list[str] = []
    kinds = config.get("kinds", {})
    if not isinstance(kinds, dict) or not kinds:
        return [
            ng(
                "prompts-config",
                f"no prompt kinds found in {resolved_path}",
                "Add at least one kind under config/prompts.yaml.",
            )
        ]

    for kind, kind_config in kinds.items():
        if not isinstance(kind_config, dict) or "template" not in kind_config:
            missing.append(f"kinds.{kind}.template")
            continue
        template_path = resolve_project_path(str(kind_config["template"]), project_root)
        if not template_path.exists():
            missing.append(str(template_path))

    common_context = config.get("common_context", {})
    if isinstance(common_context, dict):
        for name, path_value in common_context.items():
            path = resolve_project_path(str(path_value), project_root)
            if not path.exists():
                missing.append(f"common_context.{name}={path}")

    profiles = config.get("profiles", {})
    if isinstance(profiles, dict):
        for name, profile_config in profiles.items():
            if not isinstance(profile_config, dict):
                missing.append(f"profiles.{name}")
                continue
            product_note = profile_config.get("product_note")
            if product_note:
                path = resolve_project_path(str(product_note), project_root)
                if not path.exists():
                    missing.append(f"profiles.{name}.product_note={path}")

    checks.append(ok("prompts-config", f"loaded {len(kinds)} prompt kinds from {resolved_path}"))
    if missing:
        checks.append(
            ng(
                "prompt-files",
                "missing prompt files: " + ", ".join(missing),
                "Fix config/prompts.yaml or restore the referenced prompt files.",
            )
        )
    else:
        checks.append(ok("prompt-files", "all referenced prompt files exist"))
    return checks


def check_data_root(data_root: Path) -> list[DoctorCheck]:
    missing = [name for name in DATA_DIRS if not (data_root / name).exists()]
    if not missing:
        return [ok("data-root", f"required data directories exist under {data_root}")]
    return [
        warn(
            "data-root",
            f"missing directories under {data_root}: {', '.join(missing)}",
            "They will be created automatically by render/send commands.",
        )
    ]


def check_settings_file(project_root: Path) -> list[DoctorCheck]:
    example_path = settings_example_path(project_root)
    local_path = settings_path(project_root)
    checks: list[DoctorCheck] = []

    if example_path.exists():
        checks.append(ok("settings-example", f"tracked example exists: {example_path.name}"))
    else:
        checks.append(
            ng(
                "settings-example",
                f"missing tracked example: {example_path.name}",
                "Restore settings.example.json.",
            )
        )

    if local_path.exists():
        checks.append(ok("settings-local", f"local settings exists: {local_path.name}"))
    else:
        checks.append(
            warn(
                "settings-local",
                f"local settings is missing: {local_path.name}",
                "Run `dock-windows-codex-sender settings init` if you want persistent local settings.",
            )
        )

    return checks


def check_codex_cli(codex_bin: str) -> list[DoctorCheck]:
    try:
        command_prefix = parse_command_prefix(codex_bin)
    except ValueError as exc:
        return [
            ng(
                "codex-cli",
                str(exc),
                "Set DOCK_CODEX_BIN or pass --codex-bin with a non-empty command.",
            )
        ]

    launcher = command_prefix[0]
    resolved_launcher = shutil.which(launcher)
    if resolved_launcher is None:
        return [
            ng(
                "codex-cli",
                f"launcher not found: {launcher}",
                (
                    "Set DOCK_CODEX_BIN or pass --codex-bin. "
                    'If Codex is installed only in WSL, try --codex-bin "wsl.exe /mnt/c/Users/amano/.codex/bin/wsl/codex".'
                ),
            )
        ]

    try:
        completed = subprocess.run(
            [*command_prefix, "--version"],
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=10,
            check=False,
        )
    except Exception as exc:
        return [
            ng(
                "codex-cli",
                f"launcher found but version check failed: {exc}",
                "Check DOCK_CODEX_BIN / --codex-bin and Codex CLI installation.",
            )
        ]

    output = (completed.stdout or completed.stderr).strip().splitlines()
    version = output[0] if output else "no version output"
    if completed.returncode != 0:
        return [
            ng(
                "codex-cli",
                f"version check exited with {completed.returncode}: {version}",
                "Check Codex CLI installation before running actual send.",
            )
        ]
    return [ok("codex-cli", f"version check passed: {version}")]


def check_cli_only_boundary(project_root: Path) -> list[DoctorCheck]:
    checks: list[DoctorCheck] = []

    found = [path for path in FORBIDDEN_WEB_ARTIFACTS if (project_root / path).exists()]
    if found:
        checks.append(
            ng(
                "cli-only-boundary",
                "forbidden Web/UI artifacts found: " + ", ".join(found),
                "Remove first-party Web UI artifacts from this CLI-only product.",
            )
        )
    else:
        checks.append(ok("cli-only-boundary", "no first-party Web UI artifacts found"))

    agents_path = project_root / "AGENTS.md"
    if agents_path.exists():
        checks.append(
            ng(
                "agents-policy",
                "AGENTS.md exists, but current product policy keeps it absent",
                "Remove AGENTS.md unless AGENTS maintenance is explicitly re-approved.",
            )
        )
    else:
        checks.append(ok("agents-policy", "AGENTS.md is absent as expected"))

    return checks


def run_doctor(
    *,
    repos_config: Path,
    prompts_config: Path,
    data_root: Path,
    project_root: Path,
    codex_bin: str,
) -> list[DoctorCheck]:
    checks: list[DoctorCheck] = []

    repo_checks, _ = check_repos_config(repos_config)
    checks.extend(repo_checks)
    checks.extend(check_prompts_config(prompts_config, project_root))
    checks.extend(check_data_root(data_root))
    checks.extend(check_settings_file(project_root))
    checks.extend(check_codex_cli(codex_bin))
    checks.extend(check_cli_only_boundary(project_root))

    return checks
