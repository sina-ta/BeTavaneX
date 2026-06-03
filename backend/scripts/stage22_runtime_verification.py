#!/usr/bin/env python3
"""Stage 22 automated runtime verification (role + optional PostgreSQL E2E)."""

from __future__ import annotations

import os
import subprocess
import sys


def main() -> int:
    os.environ.setdefault("SKIP_STARTUP_VALIDATION", "true")
    scripts = [
        "backend/scripts/stage19_pilot_validation.py",
        "backend/scripts/stage21_pilot_validation.py",
    ]
    env = {**os.environ, "PYTHONPATH": "."}
    for script in scripts:
        print(f"Running {script}...")
        result = subprocess.run(
            [sys.executable, script],
            env=env,
            check=False,
        )
        if result.returncode != 0:
            print(f"{script} failed")
            return result.returncode

    if os.getenv("RUN_POSTGRES_VALIDATION", "").lower() in {"1", "true", "yes"}:
        print("Running backend/scripts/stage22_postgres_validation.py...")
        pg = subprocess.run(
            [sys.executable, "backend/scripts/stage22_postgres_validation.py"],
            env=env,
            check=False,
        )
        if pg.returncode != 0:
            return pg.returncode

    print("Stage 22 runtime verification passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
