from pathlib import Path

from dock_for_windows_codex_sender.models import RepoConfig
from dock_for_windows_codex_sender.render import render_prompt, simple_render


def test_simple_render_nested_dict():
    rendered = simple_render("hello {{ repo.name }}", {"repo": {"name": "Example"}})
    assert rendered == "hello Example"


def test_render_prompt_bootstrap():
    project_root = Path(__file__).resolve().parents[1]
    prompts_config = {
        "kinds": {"bootstrap": {"template": "prompts/kinds/bootstrap.md"}},
        "common_context": {
            "timeline_operating_context": "prompts/common/timeline_operating_context.md",
            "send_verification_block": "prompts/common/send_verification_block.md",
        },
        "profiles": {
            "dock_for_windows_codex_sender": {
                "product_note": "prompts/products/dock_for_windows_codex_sender.md"
            }
        },
    }
    repo = RepoConfig(
        repo_id="dock_for_windows_codex_sender",
        name="DockForWindowsCodexSender",
        path=project_root,
        product_family="dock",
        priority="high",
        prompt_profile="dock_for_windows_codex_sender",
    )
    rendered = render_prompt(
        repo=repo,
        kind="bootstrap",
        prompts_config=prompts_config,
        project_root=project_root,
        run_id="run-test-001",
        rendered_at="2026-04-27T12:34:56+09:00",
    )
    assert "DockForWindowsCodexSender" in rendered.content
    assert "Send-only" in rendered.content or "send-only" in rendered.content
    assert "run-test-001" in rendered.content
    assert rendered.prompt_sha256
