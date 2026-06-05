#!/usr/bin/env bash
set -euo pipefail

cd /app

echo "[entrypoint] Waiting for PostgreSQL..."
python - <<'PY'
import os
import sys
import time

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from backend.config import get_settings

settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)
deadline = time.time() + int(os.getenv("DB_WAIT_SECONDS", "60"))

while time.time() < deadline:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("[entrypoint] PostgreSQL is ready.")
        sys.exit(0)
    except SQLAlchemyError as exc:
        print(f"[entrypoint] DB not ready: {exc}")
        time.sleep(2)

print("[entrypoint] PostgreSQL wait timed out.", file=sys.stderr)
sys.exit(1)
PY

# Schema: Alembic only (do not run phase1_init_schema.py here — it duplicates
# tables already created by migration 20260603_0000 / 0001 / 0003).
if [[ "${RUN_SCHEMA_BOOTSTRAP:-false}" == "true" ]]; then
  echo "[entrypoint] WARNING: RUN_SCHEMA_BOOTSTRAP=true is deprecated in Docker."
  echo "[entrypoint] Running manual create_all (phase1_init_schema.py)..."
  python backend/scripts/phase1_init_schema.py
fi

if [[ "${RUN_ALEMBIC_UPGRADE:-true}" == "true" ]]; then
  echo "[entrypoint] Applying Alembic migrations (single schema source)..."
  alembic -c backend/alembic.ini upgrade head
fi

if [[ "${RUN_SEED_PLATFORM_USERS:-true}" == "true" ]]; then
  echo "[entrypoint] Seeding platform users..."
  python backend/scripts/seed_platform_users.py
fi

echo "[entrypoint] Starting API..."
exec "$@"
