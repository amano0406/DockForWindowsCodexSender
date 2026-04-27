from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RepoConfig:
    repo_id: str
    name: str
    path: Path
    product_family: str
    priority: str
    prompt_profile: str
    enabled: bool = True


@dataclass(frozen=True)
class RenderedPrompt:
    repo_id: str
    kind: str
    run_id: str
    rendered_at: str
    prompt_sha256: str
    content: str


@dataclass(frozen=True)
class SendResult:
    repo_id: str
    kind: str
    run_id: str
    prompt_sha256: str
    outbox_path: Path
    sent_path: Path | None
    observed_thread_id: str | None
    observed_session_path: Path | None
    transport: str
    dry_run: bool
    status: str
    command: list[str]
    returncode: int | None = None
    error: str | None = None
