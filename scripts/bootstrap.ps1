$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ReposConfig = Join-Path $RepoRoot "config\repos.yaml"
$ReposExample = Join-Path $RepoRoot "config\repos.example.yaml"

if (-not (Test-Path $ReposConfig)) {
  Copy-Item $ReposExample $ReposConfig
}

& "$PSScriptRoot\docker.ps1" settings init
& "$PSScriptRoot\docker-test.ps1"
