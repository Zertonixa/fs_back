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

RUN pip install --no-cache-dir uv

COPY pyproject.toml .
COPY uv.lock .

RUN uv pip install --editable . --system

# ========== FINAL ==========
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /usr/local /usr/local
COPY ./src ./src
COPY ./config.toml ./config.toml
COPY .env .env

COPY ./alembic.ini ./alembic.ini
COPY ./alembic ./alembic

COPY infra/entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

CMD ["./entrypoint.sh"]
