# Dockerfile for Telegram Bot
# Uses uv for dependency management

ARG REGISTRY_PREFIX=harbor.pg.innopolis.university/docker-hub-cache/

# ---
# Stage 1: Build the application
# ---
FROM ${REGISTRY_PREFIX}astral/uv:python3.14-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Copy root uv.lock and bot pyproject.toml
COPY uv.lock pyproject.toml /app/
COPY bot/pyproject.toml /app/bot/pyproject.toml
COPY bot/ /app/bot/

# Sync dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --package se-toolkit-lab-7-bot

# ---
# Stage 2: Runtime image
# ---
FROM ${REGISTRY_PREFIX}python:3.14.2-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Non-root user
RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

# Copy application from builder
COPY --from=builder --chown=nonroot:nonroot /app /app

# Add venv to PATH
ENV PATH="/app/.venv/bin:$PATH"

USER nonroot

WORKDIR /app

# Run the bot with Python
CMD ["python", "bot/bot.py"]
