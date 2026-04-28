FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DOCK_CODEX_IN_DOCKER=1
ENV PYTHONPATH=/mnt/c/apps/DockForWindowsCodexSender/src

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir -e ".[dev]"

WORKDIR /mnt/c/apps/DockForWindowsCodexSender

ENTRYPOINT ["dock-windows-codex-sender"]
