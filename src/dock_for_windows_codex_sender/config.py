from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import RepoConfig


def resolve_config_path(config_path: Path, *, example_name: str | None = None) -> Path:
    if config_path.exists():
        return config_path

    if example_name and config_path.name.endswith(".yaml"):
        fallback = config_path.with_name(example_name)
        if fallback.exists():
            return fallback

    raise FileNotFoundError(f"Config file not found: {config_path}")


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Config file must contain a mapping: {path}")
    return data


def load_repos(config_path: Path) -> dict[str, RepoConfig]:
    resolved_path = resolve_config_path(config_path, example_name="repos.example.yaml")
    data = load_yaml(resolved_path)
    repos = data.get("repos")
    if not isinstance(repos, dict):
        raise ValueError(f"`repos` mapping is missing in {resolved_path}")

    result: dict[str, RepoConfig] = {}
    base_dir = resolved_path.parent.parent.resolve()

    for repo_id, raw in repos.items():
        if not isinstance(raw, dict):
            raise ValueError(f"Repo config must be a mapping: {repo_id}")
        path = Path(str(raw["path"]))
        if not path.is_absolute():
            path = (base_dir / path).resolve()
        result[repo_id] = RepoConfig(
            repo_id=repo_id,
            name=str(raw.get("name", repo_id)),
            path=path,
            product_family=str(raw.get("product_family", "")),
            priority=str(raw.get("priority", "")),
            prompt_profile=str(raw.get("prompt_profile", "")),
            enabled=bool(raw.get("enabled", True)),
        )
    return result


def load_prompts(config_path: Path) -> dict[str, Any]:
    resolved_path = resolve_config_path(config_path, example_name="prompts.example.yaml")
    return load_yaml(resolved_path)
