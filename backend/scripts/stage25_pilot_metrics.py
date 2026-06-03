#!/usr/bin/env python3
"""Summarize Stage 25 pilot metrics JSON (from controlled_pilot_simulation)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def _load_metrics(path: Path) -> dict:
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    metrics_path = Path(
        os.getenv(
            "STAGE25_METRICS_PATH",
            root / "data" / "stage25_metrics.json",
        ),
    )

    if not metrics_path.is_file():
        print("Generating metrics via stage25_controlled_pilot_simulation.py...")
        env = {
            **os.environ,
            "PYTHONPATH": str(root),
            "SKIP_STARTUP_VALIDATION": "true",
            "STAGE25_METRICS_PATH": str(metrics_path),
        }
        subprocess.run(
            [sys.executable, "backend/scripts/stage25_controlled_pilot_simulation.py"],
            cwd=root,
            env=env,
            check=False,
        )

    metrics = _load_metrics(metrics_path)
    if not metrics:
        print("No Stage 25 metrics file found.")
        return 1

    timings = metrics.get("timings_ms", {})
    print("Stage 25 pilot metrics summary")
    print(f"  database_available: {metrics.get('database_available')}")
    print(f"  conflicts (409): {metrics.get('conflicts', 0)}")
    print(f"  errors: {len(metrics.get('errors', []))}")

    if timings:
        print("\n  Timings (ms):")
        for key in sorted(timings):
            print(f"    {key}: {timings[key]}")

    workflow_ms = (
        timings.get("create_workflow_step", 0)
        + timings.get("create_work_order", 0)
        + timings.get("assign_work_order", 0)
    )
    if workflow_ms:
        print(f"\n  Approx. time to create workflow (planning+assign): {workflow_ms:.0f} ms")

    report_ms = timings.get("submit_daily_report")
    approve_ms = timings.get("approve_workflow_step")
    dash_ms = timings.get("dashboard_summary")

    if report_ms is not None:
        print(f"  Time to submit report: {report_ms} ms")
    if approve_ms is not None:
        print(f"  Approval latency (API): {approve_ms} ms")
    if dash_ms is not None:
        print(f"  Dashboard summary (API): {dash_ms} ms")

    return 0 if not metrics.get("errors") else 1


if __name__ == "__main__":
    sys.exit(main())
