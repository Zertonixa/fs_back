#!/bin/bash

set -e

ENV=${1:-dev}
CMD=${2:-up}

COMPOSE_FILE="infra/${ENV}/docker-compose.yml"

if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "❌ No compose file found for env: $ENV"
  exit 1
fi

if [[ "$CMD" == "up" ]]; then
  echo "🚀 Starting $ENV environment..."
  docker compose -f "$COMPOSE_FILE" up --build
elif [[ "$CMD" == "down" ]]; then
  echo "🧹 Stopping $ENV environment..."
  docker compose -f "$COMPOSE_FILE" down
elif [[ "$CMD" == "build" ]]; then
  echo "🔧 Building $ENV environment..."
  docker compose -f "$COMPOSE_FILE" build
elif [[ "$CMD" == "logs" ]]; then
  docker compose -f "$COMPOSE_FILE" logs -f
elif [[ "$CMD" == "ps" ]]; then
  docker compose -f "$COMPOSE_FILE" ps
else
  echo "Usage: run.sh [env] [up|down|build|logs|ps]"
  echo "Example: run.sh dev up"
  exit 1
fi
