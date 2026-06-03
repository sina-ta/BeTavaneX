#!/usr/bin/env python3
"""Stage 32 verification orchestrator."""

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
        "backend/scripts/stage31_verification.py",
        "backend/scripts/stage32_verification.py",
    ):
        if _run(script) != 0:
            return 1
    print("\nStage 32 runtime verification passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
