#!/usr/bin/env python3
"""Stage 24 Alembic repeatability: upgrade head, downgrade latest, re-upgrade."""

from __future__ import annotations

import os
import subprocess
import sys

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

os.environ.setdefault("SKIP_STARTUP_VALIDATION", "true")

from backend.config import get_settings  # noqa: E402

_ALEMBIC = ["alembic", "-c", "backend/alembic.ini"]
_EXPECTED_HEAD = "20260603_0003"


def _run(args: list[str]) -> int:
    result = subprocess.run(args, check=False)
    return result.returncode


def main() -> int:
    settings = get_settings()
    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        print(f"PostgreSQL unavailable: {exc}")
        return 1

    steps = [
        ("upgrade head", _ALEMBIC + ["upgrade", "head"]),
        ("downgrade -1", _ALEMBIC + ["downgrade", "-1"]),
        ("upgrade head (repeat)", _ALEMBIC + ["upgrade", "head"]),
    ]
    for label, cmd in steps:
        print(f"Alembic: {label}...")
        if _run(cmd) != 0:
            print(f"Alembic step failed: {label}")
            return 1

    try:
        with engine.connect() as connection:
            tables = {
                row[0]
                for row in connection.execute(
                    text(
                        """
                        SELECT tablename FROM pg_tables
                        WHERE schemaname = 'public'
                          AND tablename IN (
                            'platform_users',
                            'project_memberships'
                          )
                        """,
                    ),
                ).fetchall()
            }
            if "platform_users" not in tables:
                print("Missing table platform_users after upgrade")
                return 1
            if "project_memberships" not in tables:
                print("Missing table project_memberships after upgrade")
                return 1

            version = connection.execute(
                text("SELECT version_num FROM alembic_version"),
            ).scalar()
            if version != _EXPECTED_HEAD:
                print(f"Expected head {_EXPECTED_HEAD}, got {version}")
                return 1
    except SQLAlchemyError as exc:
        print(f"Post-migration verification failed: {exc}")
        return 1

    print(f"Stage 24 Alembic validation passed (head={_EXPECTED_HEAD}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
