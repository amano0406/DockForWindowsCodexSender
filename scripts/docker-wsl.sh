#!/usr/bin/env bash
set -euo pipefail

skip_build=0
if [[ "${1:-}" == "--skip-build" ]]; then
  skip_build=1
  shift
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "${script_dir}/.." && pwd)"
apps_root="$(cd -- "${repo_root}/.." && pwd)"

image_name="${DOCK_CODEX_IMAGE:-dock-for-windows-codex-sender:local}"
windows_user="${DOCK_CODEX_WINDOWS_USER:-${USERNAME:-amano}}"
codex_home="${DOCK_CODEX_CODEX_HOME:-/mnt/c/Users/${windows_user}/.codex}"

if [[ "${skip_build}" == "0" ]]; then
  docker build -t "${image_name}" "${repo_root}"
fi

if [[ "$#" == "0" ]]; then
  set -- doctor
fi

docker run --rm \
  -e DOCK_CODEX_IN_DOCKER=1 \
  -v "${apps_root}:/mnt/c/apps" \
  -v "${codex_home}:/mnt/c/Users/${windows_user}/.codex" \
  -w /mnt/c/apps/DockForWindowsCodexSender \
  "${image_name}" "$@"
