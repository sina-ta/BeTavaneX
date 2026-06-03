#!/usr/bin/env python3
"""Stage 23 automated verification orchestrator."""

from __future__ import annotations

import os
import subprocess
import sys


def _run(script: str) -> int:
    print(f"\n=== {script} ===")
    result = subprocess.run(
        [sys.executable, script],
        env={**os.environ, "PYTHONPATH": "."},
        check=False,
    )
    return result.returncode


def main() -> int:
    os.environ.setdefault("SKIP_STARTUP_VALIDATION", "true")

    scripts = [
        "backend/scripts/stage22_runtime_verification.py",
        "backend/scripts/stage22_integrity_audit.py",
        "backend/scripts/stage23_deployment_verification.py",
        "backend/scripts/stage23_stress_simulation.py",
    ]

    for script in scripts:
        if _run(script) != 0:
            print(f"{script} failed")
            return 1

    if os.getenv("RUN_POSTGRES_VALIDATION", "").lower() in {"1", "true", "yes"}:
        for script in (
            "backend/scripts/stage22_postgres_validation.py",
            "backend/scripts/stage23_postgres_performance_audit.py",
        ):
            if _run(script) != 0:
                return 1

    print("\nStage 23 runtime verification passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
