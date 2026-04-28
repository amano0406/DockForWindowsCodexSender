param(
  [switch] $SkipBuild,

  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]] $CliArgs
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$AppsRoot = (Resolve-Path (Join-Path $RepoRoot "..")).Path
$ImageName = "dock-for-windows-codex-sender:local"
$UserName = if ($env:USERNAME) { $env:USERNAME } else { "amano" }
$CodexHome = Join-Path $env:USERPROFILE ".codex"

if (-not $SkipBuild) {
  docker build -t $ImageName $RepoRoot | Out-Host
}

$argsList = @(
  "run",
  "--rm",
  "-e", "DOCK_CODEX_IN_DOCKER=1",
  "-v", "${AppsRoot}:/mnt/c/apps",
  "-v", "${CodexHome}:/mnt/c/Users/${UserName}/.codex",
  "-w", "/mnt/c/apps/DockForWindowsCodexSender",
  $ImageName
)

if ($CliArgs.Count -eq 0) {
  $CliArgs = @("doctor")
}

docker @argsList @CliArgs
