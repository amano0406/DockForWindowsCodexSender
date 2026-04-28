from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SETTINGS_EXAMPLE_NAME = "settings.example.json"
SETTINGS_NAME = "settings.json"


@dataclass(frozen=True)
class AppSettings:
    version: int = 1
    repos_config: str = "config/repos.yaml"
    prompts_config: str = "config/prompts.yaml"
    data_root: str = "data"
    codex_bin: str = ""


def settings_path(project_root: Path) -> Path:
    return project_root / SETTINGS_NAME


def settings_example_path(project_root: Path) -> Path:
    return project_root / SETTINGS_EXAMPLE_NAME


def app_settings_from_mapping(data: dict[str, Any]) -> AppSettings:
    return AppSettings(
        version=int(data.get("version", 1)),
        repos_config=str(data.get("repos_config", "config/repos.yaml")),
        prompts_config=str(data.get("prompts_config", "config/prompts.yaml")),
        data_root=str(data.get("data_root", "data")),
        codex_bin=str(data.get("codex_bin", "")),
    )


def read_settings_file(path: Path) -> AppSettings:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Settings file must contain a JSON object: {path}")
    return app_settings_from_mapping(data)


def load_settings(project_root: Path) -> AppSettings:
    path = settings_path(project_root)
    if path.exists():
        return read_settings_file(path)
    return AppSettings()


def load_settings_example(project_root: Path) -> dict[str, Any]:
    path = settings_example_path(project_root)
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"Settings example must contain a JSON object: {path}")
        return data
    return {
        "version": 1,
        "repos_config": "config/repos.yaml",
        "prompts_config": "config/prompts.yaml",
        "data_root": "data",
        "codex_bin": "",
    }


def init_settings_file(
    *,
    project_root: Path,
    overrides: dict[str, str] | None = None,
) -> tuple[Path, bool]:
    path = settings_path(project_root)
    if path.exists():
        return path, False

    data = load_settings_example(project_root)
    if overrides:
        for key, value in overrides.items():
            if value:
                data[key] = value

    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path, True
