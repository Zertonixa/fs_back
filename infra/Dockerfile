# ========== BUILDER ==========
FROM python:3.12-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_HTTP_TIMEOUT=120
ENV UV_HTTP_RETRIES=10
ENV UV_LINK_MODE=copy

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends gcc libpq-dev; \
    rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir uv

COPY pyproject.toml ./
COPY uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# ========== FINAL ==========
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY --from=builder /app/.venv /app/.venv

COPY ./src ./src
COPY ./alembic.ini ./alembic.ini
COPY ./alembic ./alembic

COPY infra/entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

CMD ["./entrypoint.sh"]