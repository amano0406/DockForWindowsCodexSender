$ErrorActionPreference = "Stop"

& "$PSScriptRoot\docker.ps1" doctor
& "$PSScriptRoot\docker.ps1" repos list
& "$PSScriptRoot\docker.ps1" prompt render --repo dock_for_windows_codex_sender --kind bootstrap
& "$PSScriptRoot\docker.ps1" send --repo dock_for_windows_codex_sender --kind bootstrap --dry-run
& "$PSScriptRoot\docker-test.ps1"
