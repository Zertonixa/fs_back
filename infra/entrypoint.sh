#!/bin/sh
set -e

echo "[$(date)] run alembic migrations..."
alembic upgrade head

echo "[$(date)] start app..."
exec python -m src.api
