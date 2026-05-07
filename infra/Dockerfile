# ========== BUILDER ==========
FROM python:3.12-slim AS builder

WORKDIR /app

RUN set -eux; \
    echo "deb https://deb.debian.org/debian trixie main" > /etc/apt/sources.list; \
    echo "deb https://deb.debian.org/debian trixie-updates main" >> /etc/apt/sources.list; \
    echo "deb https://deb.debian.org/debian-security trixie-security main" >> /etc/apt/sources.list; \
    apt-get update; \
    apt-get install -y --no-install-recommends gcc libpq-dev; \
    rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install uv

COPY pyproject.toml ./
COPY uv.lock ./

ENV UV_HTTP_TIMEOUT=120
ENV UV_HTTP_RETRIES=10

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# ========== FINAL ==========
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY ./src ./src
COPY ./alembic.ini ./alembic.ini
COPY ./alembic ./alembic

COPY infra/entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

CMD ["./entrypoint.sh"]
