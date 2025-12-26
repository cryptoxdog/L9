#!/usr/bin/env bash
set -euo pipefail

# Directory where your docker-compose.yml lives
APP_DIR="/opt/l9"   # adjust if your repo is elsewhere

SERVICE="l9-api"
COMPOSE_FILE="docker-compose.yml"

cd "$APP_DIR"

echo "[deploy] Using compose file: $APP_DIR/$COMPOSE_FILE"
echo "[deploy] WARNING: If docker-compose.override.yml exists, it will be auto-merged"
docker compose -f "$COMPOSE_FILE" config

echo "[deploy] Building image for $SERVICE..."
docker compose -f "$COMPOSE_FILE" build "$SERVICE"

echo "[deploy] Ensuring stack is up at least once..."
docker compose -f "$COMPOSE_FILE" up -d

echo "[deploy] Rolling out zero-downtime update for $SERVICE..."
docker rollout -f "$COMPOSE_FILE" "$SERVICE"

echo "[deploy] Done. Current containers:"
docker compose -f "$COMPOSE_FILE" ps
