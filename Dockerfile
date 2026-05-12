# syntax=docker/dockerfile:1
# ── Builder: install deps with uv ─────────────────────────────────────────────
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project
# DEBUG: 看 venv 到底在哪
RUN ls -la /app && echo "---" && ls -la /app/.venv 2>/dev/null || echo "no .venv at /app/.venv" && echo "---" && find / -name "discord" -type d 2>/dev/null | head -5
COPY . .

# ── Runner ───────────────────────────────────
FROM python:3.12-slim-bookworm
WORKDIR /app
COPY --from=builder /app /app
ENV PATH="/app/.venv/bin:$PATH"
RUN test -f /app/.venv/bin/python || (echo "ERROR: .venv missing" && ls -la /app && exit 1)
CMD ["/app/.venv/bin/python", "bot.py"]