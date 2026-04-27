. .\.venv\Scripts\Activate.ps1
dock-windows-codex-sender repos list
dock-windows-codex-sender prompt render --repo dock_for_windows_codex_sender --kind bootstrap
dock-windows-codex-sender send --repo dock_for_windows_codex_sender --kind bootstrap --dry-run
pytest
