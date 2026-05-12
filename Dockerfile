# syntax=docker/dockerfile:1

# ── Builder: install deps with uv ─────────────────────────────────────────────
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

# Compile .pyc files and copy files instead of symlinking (required for COPY --from)
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Install dependencies only (cached layer — rebuilt only when lock file changes)
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Copy source after deps so the dep layer is cached on code-only changes
COPY . .

# ── Runner: slim image with no build tooling ───────────────────────────────────
FROM python:3.12-slim-bookworm

WORKDIR /app

COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "bot.py"]
