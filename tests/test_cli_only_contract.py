from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_repository_does_not_contain_first_party_web_ui_artifacts() -> None:
    forbidden_paths = [
        "web",
        "frontend",
        "ui",
        "app",
        "docker-compose.yml",
        "docker-compose.yaml",
        "start.bat",
    ]

    found = [path for path in forbidden_paths if (REPO_ROOT / path).exists()]

    assert found == []


def test_repository_does_not_contain_agents_file_by_current_policy() -> None:
    assert not (REPO_ROOT / "AGENTS.md").exists()
