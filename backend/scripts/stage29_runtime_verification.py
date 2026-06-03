#!/usr/bin/env python3
"""Stage 29 verification orchestrator."""

from __future__ import annotations

import os
import subprocess
import sys


def _run(script: str) -> int:
    print(f"\n=== {script} ===")
    return subprocess.run(
        [sys.executable, script],
        env={**os.environ, "PYTHONPATH": "."},
        check=False,
    ).returncode


def main() -> int:
    os.environ.setdefault("SKIP_STARTUP_VALIDATION", "true")
    scripts = [
        "backend/scripts/stage28_verification.py",
        "backend/scripts/stage29_verification.py",
    ]
    for script in scripts:
        if _run(script) != 0:
            print(f"{script} failed")
            return 1
    print("\nStage 29 runtime verification passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
