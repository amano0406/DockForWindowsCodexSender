from __future__ import annotations

import argparse
import os
import subprocess
from dataclasses import replace
from pathlib import Path

from .config import load_prompts, load_repos
from .doctor import run_doctor
from .models import RenderedPrompt
from .render import render_prompt
from .runtime import enforce_cli_runtime
from .settings import init_settings_file, load_settings
from .storage import append_send_log, write_prompt_file
from .transport import default_codex_bin, send_via_codex_cli


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def as_project_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def current_settings():
    return load_settings(PROJECT_ROOT)


def default_repos_config() -> Path:
    value = os.getenv("DOCK_CODEX_REPOS_CONFIG") or current_settings().repos_config
    return as_project_path(value)


def default_prompts_config() -> Path:
    value = os.getenv("DOCK_CODEX_PROMPTS_CONFIG") or current_settings().prompts_config
    return as_project_path(value)


def default_data_root() -> Path:
    value = os.getenv("DOCK_CODEX_DATA_ROOT") or current_settings().data_root
    return as_project_path(value)


def default_codex_bin_arg() -> str:
    settings = current_settings()
    return default_codex_bin(settings.codex_bin)


def add_config_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repos-config", type=Path, default=default_repos_config())
    parser.add_argument("--prompts-config", type=Path, default=default_prompts_config())
    parser.add_argument("--data-root", type=Path, default=default_data_root())


def add_common_args(parser: argparse.ArgumentParser) -> None:
    add_config_args(parser)
    parser.add_argument("--run-id")


def get_repo_or_fail(repos, repo_id: str):
    repo = repos.get(repo_id)
    if not repo:
        available = ", ".join(sorted(repos))
        raise SystemExit(f"Unknown repo: {repo_id}. Available: {available}")
    return repo


def format_command(command: list[str]) -> str:
    return subprocess.list2cmdline(command)


def cmd_repos_list(args: argparse.Namespace) -> int:
    repos = load_repos(args.repos_config)
    for repo_id, repo in repos.items():
        status = "enabled" if repo.enabled else "disabled"
        print(f"{repo_id}\t{status}\t{repo.name}\t{repo.path}")
    return 0


def render_to_outbox(args: argparse.Namespace, repo_id: str, kind: str) -> tuple[RenderedPrompt, Path]:
    repos = load_repos(args.repos_config)
    prompts_config = load_prompts(args.prompts_config)
    repo = get_repo_or_fail(repos, repo_id)

    rendered = render_prompt(
        repo=repo,
        kind=kind,
        prompts_config=prompts_config,
        project_root=PROJECT_ROOT,
        run_id=args.run_id,
    )
    out_path = write_prompt_file(
        data_root=args.data_root,
        bucket="outbox",
        run_id=rendered.run_id,
        repo_id=repo.repo_id,
        kind=kind,
        content=rendered.content,
    )
    return rendered, out_path


def cmd_prompt_render(args: argparse.Namespace) -> int:
    rendered, path = render_to_outbox(args, args.repo, args.kind)
    print(f"repo_id={rendered.repo_id}")
    print(f"kind={rendered.kind}")
    print(f"run_id={rendered.run_id}")
    print(f"prompt_sha256={rendered.prompt_sha256}")
    print(f"prompt_path={path}")
    if args.print:
        print(path.read_text(encoding="utf-8"))
    return 0


def cmd_prompt_render_all(args: argparse.Namespace) -> int:
    repos = load_repos(args.repos_config)
    for repo_id, repo in repos.items():
        if not repo.enabled:
            continue
        sub_args = argparse.Namespace(**vars(args))
        if args.run_id:
            sub_args.run_id = f"{args.run_id}-{repo_id}"
        rendered, path = render_to_outbox(sub_args, repo_id, args.kind)
        print(f"repo_id={rendered.repo_id}")
        print(f"kind={rendered.kind}")
        print(f"run_id={rendered.run_id}")
        print(f"prompt_sha256={rendered.prompt_sha256}")
        print(f"prompt_path={path}")
    return 0


def cmd_send(args: argparse.Namespace) -> int:
    repos = load_repos(args.repos_config)
    prompts_config = load_prompts(args.prompts_config)
    repo = get_repo_or_fail(repos, args.repo)

    rendered = render_prompt(
        repo=repo,
        kind=args.kind,
        prompts_config=prompts_config,
        project_root=PROJECT_ROOT,
        run_id=args.run_id,
    )

    outbox_path = write_prompt_file(
        data_root=args.data_root,
        bucket="outbox",
        run_id=rendered.run_id,
        repo_id=repo.repo_id,
        kind=args.kind,
        content=rendered.content,
    )

    result = send_via_codex_cli(
        repo=repo,
        kind=args.kind,
        run_id=rendered.run_id,
        prompt_sha256=rendered.prompt_sha256,
        outbox_path=outbox_path,
        prompt_text=rendered.content,
        codex_bin=args.codex_bin,
        resume_session=args.resume,
        resume_last=args.resume_last,
        dry_run=args.dry_run,
    )

    if result.status == "sent":
        sent_path = write_prompt_file(
            data_root=args.data_root,
            bucket="sent",
            run_id=rendered.run_id,
            repo_id=repo.repo_id,
            kind=args.kind,
            content=rendered.content,
        )
        result = replace(result, sent_path=sent_path)

    append_send_log(data_root=args.data_root, result=result)

    print(f"repo_id={result.repo_id}")
    print(f"kind={result.kind}")
    print(f"run_id={result.run_id}")
    print(f"prompt_sha256={result.prompt_sha256}")
    print(f"status={result.status}")
    print(f"outbox_path={result.outbox_path}")
    if result.sent_path:
        print(f"sent_path={result.sent_path}")
    if result.observed_thread_id:
        print(f"observed_thread_id={result.observed_thread_id}")
    if result.observed_session_path:
        print(f"observed_session_path={result.observed_session_path}")
    print("command=" + format_command(result.command))
    if result.error:
        print(f"error={result.error}")
    return 0 if result.status in {"dry-run", "sent"} else 1


def cmd_send_all(args: argparse.Namespace) -> int:
    if not args.dry_run and not args.confirm_send_all:
        raise SystemExit("Refusing actual send-all without --confirm-send-all.")

    repos = load_repos(args.repos_config)
    exit_code = 0
    for repo_id, repo in repos.items():
        if not repo.enabled:
            continue
        sub_args = argparse.Namespace(**vars(args))
        if args.run_id:
            sub_args.run_id = f"{args.run_id}-{repo_id}"
        sub_args.repo = repo_id
        try:
            rc = cmd_send(sub_args)
            exit_code = max(exit_code, rc)
        except Exception as exc:
            exit_code = 1
            print(f"[ERROR] {repo_id}: {exc}")
    return exit_code


def cmd_doctor(args: argparse.Namespace) -> int:
    checks = run_doctor(
        repos_config=args.repos_config,
        prompts_config=args.prompts_config,
        data_root=args.data_root,
        project_root=PROJECT_ROOT,
        codex_bin=args.codex_bin,
    )

    has_ng = False
    for check in checks:
        if check.status == "NG":
            has_ng = True
        print(f"{check.status}\t{check.name}\t{check.message}")
        if check.action:
            print(f"ACTION\t{check.name}\t{check.action}")

    return 1 if has_ng else 0


def cmd_settings_init(args: argparse.Namespace) -> int:
    path, created = init_settings_file(
        project_root=PROJECT_ROOT,
        overrides={"codex_bin": default_codex_bin()},
    )
    status = "created" if created else "exists"
    print(f"status={status}")
    print(f"settings_path={path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dock-windows-codex-sender")
    sub = parser.add_subparsers(dest="command", required=True)

    repos = sub.add_parser("repos")
    repos_sub = repos.add_subparsers(dest="repos_command", required=True)
    repos_list = repos_sub.add_parser("list")
    add_common_args(repos_list)
    repos_list.set_defaults(func=cmd_repos_list)

    prompt = sub.add_parser("prompt")
    prompt_sub = prompt.add_subparsers(dest="prompt_command", required=True)

    prompt_render = prompt_sub.add_parser("render")
    add_common_args(prompt_render)
    prompt_render.add_argument("--repo", required=True)
    prompt_render.add_argument("--kind", required=True)
    prompt_render.add_argument("--print", action="store_true")
    prompt_render.set_defaults(func=cmd_prompt_render)

    prompt_render_all = prompt_sub.add_parser("render-all")
    add_common_args(prompt_render_all)
    prompt_render_all.add_argument("--kind", required=True)
    prompt_render_all.set_defaults(func=cmd_prompt_render_all)

    send = sub.add_parser("send")
    add_common_args(send)
    send.add_argument("--repo", required=True)
    send.add_argument("--kind", required=True)
    send.add_argument("--dry-run", action="store_true")
    send.add_argument("--codex-bin", default=default_codex_bin_arg())
    resume_group = send.add_mutually_exclusive_group()
    resume_group.add_argument("--resume")
    resume_group.add_argument("--resume-last", action="store_true")
    send.set_defaults(func=cmd_send)

    send_all = sub.add_parser("send-all")
    add_common_args(send_all)
    send_all.add_argument("--kind", required=True)
    send_all.add_argument("--dry-run", action="store_true")
    send_all.add_argument("--confirm-send-all", action="store_true")
    send_all.add_argument("--codex-bin", default=default_codex_bin_arg())
    send_all.set_defaults(func=cmd_send_all)

    doctor = sub.add_parser("doctor")
    add_config_args(doctor)
    doctor.add_argument("--codex-bin", default=default_codex_bin_arg())
    doctor.set_defaults(func=cmd_doctor)

    settings = sub.add_parser("settings")
    settings_sub = settings.add_subparsers(dest="settings_command", required=True)
    settings_init = settings_sub.add_parser("init")
    settings_init.set_defaults(func=cmd_settings_init)

    return parser


def main() -> None:
    enforce_cli_runtime()
    parser = build_parser()
    args = parser.parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
