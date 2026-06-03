#!/usr/bin/env python3
"""Stage 26 verification — feedback synthesis + prior pilot scripts."""

from __future__ import annotations

import os
import subprocess
import sys


def main() -> int:
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env = {**os.environ, "PYTHONPATH": root, "SKIP_STARTUP_VALIDATION": "true"}
    scripts = ["backend/scripts/stage26_feedback_synthesis.py"]
    for script in scripts:
        print(f"Running {script}...")
        result = subprocess.run(
            [sys.executable, script],
            cwd=root,
            env=env,
            check=False,
        )
        if result.returncode != 0:
            return result.returncode
    print("Stage 26 operational verification passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
