#!/usr/bin/env bash
# Run the seed pipeline once against the Railway MySQL service.
#
# Usage:
#   1. Fill in the five Railway values below (or export them in your shell
#      before running this script).
#   2. ./scripts/seed-railway.sh
#
# The script runs the seed inside the local `api` Docker image, so you
# don't need Python/MySQL on your host. The local Redis is brought up
# only to satisfy the app's required env vars; the seed itself doesn't
# touch Redis.
#
# Safe to run more than once — INSERT IGNORE / dedup logic in the
# seeders means a re-run will not duplicate rows.

set -euo pipefail

# ── Fill these in (or export before running) ────────────────────────────────
: "${DB_HOST:=PASTE_RAILWAY_MYSQLHOST_HERE}"
: "${DB_PORT:=PASTE_RAILWAY_MYSQLPORT_HERE}"
: "${DB_USER:=PASTE_RAILWAY_MYSQLUSER_HERE}"
: "${DB_PASSWORD:=PASTE_RAILWAY_MYSQLPASSWORD_HERE}"
: "${DB_NAME:=PASTE_RAILWAY_MYSQLDATABASE_HERE}"
# ────────────────────────────────────────────────────────────────────────────

if [[ "${DB_HOST}" == PASTE_* ]]; then
  echo "ERROR: edit scripts/seed-railway.sh and paste your Railway MySQL"
  echo "       public connection details, or export them in your shell." >&2
  exit 1
fi

cd "$(dirname "$0")/.."

echo "==> Bringing up local Redis (needed only for app config validation)"
docker compose up -d redis

echo "==> Running seed against Railway MySQL at ${DB_HOST}:${DB_PORT}"
docker compose run --rm \
  -e DB_HOST="${DB_HOST}" \
  -e DB_PORT="${DB_PORT}" \
  -e DB_USER="${DB_USER}" \
  -e DB_PASSWORD="${DB_PASSWORD}" \
  -e DB_NAME="${DB_NAME}" \
  -e SECRET_KEY=seed-only \
  -e JWT_SECRET=seed-only \
  -e REDIS_URL=redis://redis:6379/0 \
  -e CELERY_BROKER_URL=redis://redis:6379/1 \
  -e CELERY_RESULT_BACKEND=redis://redis:6379/2 \
  -e RUN_MIGRATIONS=0 \
  api python -m seed.seed_runner

echo "==> Done. Stopping local Redis."
docker compose down
