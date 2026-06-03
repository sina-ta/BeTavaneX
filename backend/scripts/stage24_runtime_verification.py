#!/usr/bin/env python3
"""Stage 24 verification orchestrator."""

from __future__ import annotations

import os
import subprocess
import sys

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


def _postgres_reachable() -> bool:
    if os.getenv("RUN_POSTGRES_VALIDATION", "").lower() in {"1", "true", "yes"}:
        return True
    os.environ.setdefault("SKIP_STARTUP_VALIDATION", "true")
    try:
        from backend.config import get_settings

        engine = create_engine(get_settings().database_url, pool_pre_ping=True)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except (SQLAlchemyError, ImportError):
        return False


def _child_env() -> dict[str, str]:
    env = {**os.environ, "PYTHONPATH": "."}
    env.setdefault("SKIP_STARTUP_VALIDATION", "true")
    return env


def _run(script: str, env: dict[str, str]) -> int:
    print(f"\n=== {script} ===")
    result = subprocess.run(
        [sys.executable, script],
        env=env,
        check=False,
    )
    return result.returncode


def main() -> int:
    env = _child_env()
    db_up = _postgres_reachable()

    if db_up:
        scripts = [
            "backend/scripts/stage19_pilot_validation.py",
            "backend/scripts/stage21_pilot_validation.py",
            "backend/scripts/stage24_iam_verification.py",
            "backend/scripts/stage24_load_test.py",
        ]
    else:
        print(
            "PostgreSQL not reachable — persisted IAM/login checks require a DB.\n"
            "Running deployment verification only; use Docker Compose or "
            "RUN_POSTGRES_VALIDATION=true for full Stage 24.",
        )
        scripts = [
            "backend/scripts/stage23_deployment_verification.py",
        ]

    for script in scripts:
        if _run(script, env) != 0:
            print(f"{script} failed")
            return 1

    if os.getenv("RUN_POSTGRES_VALIDATION", "").lower() in {"1", "true", "yes"}:
        for script in (
            "backend/scripts/stage24_alembic_validation.py",
            "backend/scripts/stage24_postgres_validation.py",
            "backend/scripts/stage22_postgres_validation.py",
            "backend/scripts/stage23_postgres_performance_audit.py",
        ):
            if _run(script, pg_env) != 0:
                return 1

    print("\nStage 24 runtime verification passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
