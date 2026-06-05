#!/usr/bin/env python3
"""Verify Alembic-only schema path (no duplicate project_memberships)."""

from __future__ import annotations

import os
import subprocess
import sys

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

os.environ.setdefault("SKIP_STARTUP_VALIDATION", "true")

from backend.config import get_settings  # noqa: E402

_ALEMBIC = ["alembic", "-c", "backend/alembic.ini"]


def main() -> int:
    settings = get_settings()
    engine = create_engine(settings.database_url, pool_pre_ping=True)

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        print(f"PostgreSQL unavailable: {exc}")
        return 1

    print("Docker startup schema verification")
    print("  Step 1: alembic upgrade head (first pass)")
    if subprocess.run(_ALEMBIC + ["upgrade", "head"], check=False).returncode != 0:
        return 1

    print("  Step 2: alembic upgrade head (second pass — must be idempotent)")
    if subprocess.run(_ALEMBIC + ["upgrade", "head"], check=False).returncode != 0:
        print("  FAIL: second upgrade head failed (duplicate DDL?)")
        return 1

    with engine.connect() as connection:
        version = connection.execute(
            text("SELECT version_num FROM alembic_version"),
        ).scalar()
        tables = set(inspect(connection).get_table_names())

    if version != "20260603_0005":
        print(f"  FAIL: expected head 20260603_0005, got {version}")
        return 1

    required = {"project_memberships", "platform_users", "projects"}
    missing = required - tables
    if missing:
        print(f"  FAIL: missing tables {missing}")
        return 1

    print(f"  PASS: alembic_version={version}, tables ok ({len(tables)} total)")
    print("  PASS: repeat upgrade head succeeded (no duplicate relation error)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
