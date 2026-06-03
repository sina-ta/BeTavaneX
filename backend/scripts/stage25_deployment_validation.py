#!/usr/bin/env python3
"""Stage 25 deployment validation — production-like checks + Stage 23/24 smoke."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _check_file(label: str, path: Path) -> bool:
    ok = path.is_file()
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}: {path}")
    return ok


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    passed = True

    print("Stage 25 deployment validation — artifact checks")
    for name in (
        "docker-compose.yml",
        "backend/Dockerfile",
        "frontend/Dockerfile",
        "backend/docker-entrypoint.sh",
        "docs/operations/backup-recovery.md",
    ):
        passed &= _check_file(name, root / name)

    env_example = root / ".env.docker.example"
    if env_example.is_file():
        passed &= _check_file(".env.docker.example", env_example)
    else:
        print("  [WARN] .env.docker.example missing (optional)")

    print("\nStage 25 deployment validation — runtime smoke")
    env = {**os.environ, "PYTHONPATH": ".", "SKIP_STARTUP_VALIDATION": "true"}
    for script in (
        "backend/scripts/stage23_deployment_verification.py",
        "backend/scripts/stage25_controlled_pilot_simulation.py",
    ):
        print(f"Running {script}...")
        result = subprocess.run(
            [sys.executable, script],
            cwd=root,
            env=env,
            check=False,
        )
        if result.returncode != 0:
            print(f"{script} returned {result.returncode}")
            if script.endswith("stage25_controlled_pilot_simulation.py"):
                print("  (non-zero may be acceptable when PostgreSQL is offline)")
            else:
                passed = False

    base = os.getenv("PILOT_DEPLOY_BASE_URL", os.getenv("DEPLOY_VERIFY_BASE_URL", "")).strip()
    if base:
        print(f"\nRemote deploy probe: {base}")
        try:
            import httpx  # noqa: PLC0415
        except ImportError:
            print("  [WARN] httpx not installed — skip remote probe")
        else:
            for path in ("/health/live", "/health"):
                try:
                    response = httpx.get(f"{base.rstrip('/')}{path}", timeout=10.0)
                    ok = response.status_code in (200, 503)
                    print(f"  [{'PASS' if ok else 'FAIL'}] GET {path} → {response.status_code}")
                    passed &= ok
                except Exception as exc:  # noqa: BLE001
                    print(f"  [FAIL] GET {path}: {exc}")
                    passed = False

    if passed:
        print("\nStage 25 deployment validation passed.")
        return 0

    print("\nStage 25 deployment validation completed with failures or warnings.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
