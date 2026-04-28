# Security Policy

## Baseline

- Do not store secrets in this repository.
- Do not commit `.env`.
- Do not commit `config/repos.yaml` if it contains private local paths.
- Do not log secrets, cookies, sessions, tokens, or API keys.
- Do not add a Web UI, browser frontend, dashboard, localhost service, or Docker Compose web stack.
- Do not automate Windows app UI until explicitly approved.
- Run normal CLI operations through Docker.
- Use the PowerShell Docker wrappers as the front door for normal Windows operation.
- Keep WSL/bash wrappers as a back-door route for WSL-based automation or troubleshooting, not as the default user path.
- Do not use `DOCK_CODEX_ALLOW_HOST_CLI` for normal sends; it is only for explicit test/debug exceptions.

## Sending policy

- Dry-run before actual send.
- One-repo send before send-all.
- Actual send-all requires explicit confirmation flag.
- Preserve sent prompt copies and JSONL logs.
- Preserve verification metadata such as `run_id` and `prompt_sha256`.
- Do not treat Windows app UI alone as the evidence source for sent content or file changes.

## Out of scope for v0.1

- response scraping
- browser automation
- Web UI / dashboard
- local web service
- Windows app UI automation
- automatic scheduling
- autonomous approval
