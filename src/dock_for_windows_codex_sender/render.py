from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import RenderedPrompt, RepoConfig

_VAR_RE = re.compile(r"{{\s*([a-zA-Z0-9_.]+)\s*}}")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def resolve_project_path(path_value: str, project_root: Path) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = project_root / path
    return path.resolve()


def lookup_context(context: dict[str, Any], dotted_key: str) -> str:
    current: Any = context
    for part in dotted_key.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        else:
            current = getattr(current, part, None)
        if current is None:
            return ""
    return str(current)


def simple_render(template: str, context: dict[str, Any]) -> str:
    def repl(match: re.Match[str]) -> str:
        return lookup_context(context, match.group(1))

    return _VAR_RE.sub(repl, template)


def render_with_context(template: str, context: dict[str, Any], *, passes: int = 3) -> str:
    rendered = template
    for _ in range(passes):
        next_rendered = simple_render(rendered, context)
        if next_rendered == rendered:
            return next_rendered
        rendered = next_rendered
    return rendered


def default_rendered_at() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()


def default_run_id() -> str:
    stamp = datetime.now(timezone.utc).astimezone().strftime("%Y%m%d-%H%M%S-%f")
    return f"run-{stamp}"


def build_render_context(
    *,
    repo: RepoConfig,
    kind: str,
    run_id: str,
    rendered_at: str,
    prompt_sha256: str,
    prompts_config: dict[str, Any],
    project_root: Path,
) -> dict[str, Any]:
    common_context: dict[str, str] = {}

    for name, rel_path in prompts_config.get("common_context", {}).items():
        common_context[name] = read_text(resolve_project_path(str(rel_path), project_root))

    profiles = prompts_config.get("profiles", {})
    profile = profiles.get(repo.prompt_profile, {})
    product_note_path = profile.get("product_note")
    product_note = ""
    if product_note_path:
        product_note = read_text(resolve_project_path(str(product_note_path), project_root))

    return {
        "repo": {
            "repo_id": repo.repo_id,
            "name": repo.name,
            "path": str(repo.path),
            "product_family": repo.product_family,
            "priority": repo.priority,
            "prompt_profile": repo.prompt_profile,
        },
        "kind": kind,
        "meta": {
            "run_id": run_id,
            "rendered_at": rendered_at,
            "prompt_sha256": prompt_sha256,
        },
        "common": common_context,
        "product_note": product_note,
    }


def render_prompt(
    *,
    repo: RepoConfig,
    kind: str,
    prompts_config: dict[str, Any],
    project_root: Path,
    run_id: str | None = None,
    rendered_at: str | None = None,
) -> RenderedPrompt:
    kinds = prompts_config.get("kinds", {})
    kind_config = kinds.get(kind)
    if not kind_config:
        raise KeyError(f"Unknown prompt kind: {kind}")

    resolved_run_id = run_id or default_run_id()
    resolved_rendered_at = rendered_at or default_rendered_at()
    template_path = resolve_project_path(str(kind_config["template"]), project_root)
    template = read_text(template_path)
    context = build_render_context(
        repo=repo,
        kind=kind,
        run_id=resolved_run_id,
        rendered_at=resolved_rendered_at,
        prompt_sha256="",
        prompts_config=prompts_config,
        project_root=project_root,
    )
    content = render_with_context(template, context)
    prompt_sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return RenderedPrompt(
        repo_id=repo.repo_id,
        kind=kind,
        run_id=resolved_run_id,
        rendered_at=resolved_rendered_at,
        prompt_sha256=prompt_sha256,
        content=content,
    )
