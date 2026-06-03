#!/usr/bin/env python3
"""Stage 31 verification orchestrator."""

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
    for script in (
        "backend/scripts/stage29_verification.py",
        "backend/scripts/stage31_verification.py",
    ):
        if _run(script) != 0:
            return 1
    print("\nStage 31 runtime verification passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
