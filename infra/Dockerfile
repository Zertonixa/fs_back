# ========== BUILDER ==========
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
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
COPY .env .env

CMD ["python", "-m", "src.service.main"]
