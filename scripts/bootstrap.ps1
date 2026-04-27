py -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
if (-not (Test-Path "config\repos.yaml")) {
  Copy-Item "config\repos.example.yaml" "config\repos.yaml"
}
pytest
