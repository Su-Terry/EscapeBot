# Development Guide

## Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/) — Python toolchain & package manager
- Python 3.12 (uv installs it automatically if missing)

## Setup

```bash
uv sync          # install all deps including dev (pytest etc.) into .venv
```

## Environment variables

Copy `.env.example` to `.env` (or create `.env`) and fill in:

```
GEMINI_API_KEY=...    # Google AI Studio key
BOT_TOKEN=...         # Discord bot token
```

## Running the bot

```bash
uv run python bot.py
```

## Running tests

```bash
# Unit tests only (no API key required)
uv run pytest

# Integration tests (calls Gemini API — costs tokens)
GEMINI_API_KEY=your_key uv run pytest -m integration -v
```

## Dependency management

All dependencies are declared in `pyproject.toml`. `uv.lock` pins exact versions for reproducible installs.

```bash
uv add some-package          # add a runtime dependency
uv add --dev some-package    # add a dev-only dependency
uv lock                      # regenerate lock file after manual pyproject.toml edits
```

To export a pip-compatible requirements file (e.g. for third-party tools):

```bash
uv export --format requirements-txt > requirements.txt
```

## Docker

The Dockerfile uses a two-stage build:

1. **Builder** (`ghcr.io/astral-sh/uv:python3.12-bookworm-slim`) — runs `uv sync` to populate `.venv`
2. **Runner** (`python:3.12-slim-bookworm`) — copies `.venv` + source, no build tooling

```bash
docker build -t escapebot .
docker run --env-file .env escapebot
```

## Deployment (Fly.io)

```bash
fly secrets set GEMINI_API_KEY=... BOT_TOKEN=...
fly deploy
```
