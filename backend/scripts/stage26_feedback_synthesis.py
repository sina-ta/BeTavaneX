#!/usr/bin/env python3
"""Stage 26 — synthesize pilot feedback JSONL + Stage 25/26 evidence."""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path


def _feedback_path() -> Path:
    raw = os.getenv("PILOT_FEEDBACK_PATH", "data/pilot_feedback.jsonl").strip()
    path = Path(raw)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[2] / path
    return path


def main() -> int:
    path = _feedback_path()
    categories: Counter[str] = Counter()
    roles: Counter[str] = Counter()
    entries: list[dict] = []

    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            entries.append(record)
            categories[record.get("category", "other")] += 1
            roles[record.get("role", "unknown")] += 1

    print("Stage 26 pilot feedback synthesis")
    print(f"  source: {path.name} (under data/)")
    print(f"  entries: {len(entries)}")

    if categories:
        print("  by category:")
        for key, count in categories.most_common():
            print(f"    {key}: {count}")
    if roles:
        print("  by role:")
        for key, count in roles.most_common():
            print(f"    {key}: {count}")

    if not entries:
        print(
            "  (no JSONL entries - synthesis uses Stage 25 controlled-pilot-report.md)",
        )

    metrics_path = Path(
        os.getenv(
            "STAGE25_METRICS_PATH",
            Path(__file__).resolve().parents[2] / "data" / "stage25_metrics.json",
        ),
    )
    if metrics_path.is_file():
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        timings = metrics.get("timings_ms", {})
        print(f"  stage25_metrics: database_available={metrics.get('database_available')}")
        if timings:
            print("  key timings (ms):")
            for key in (
                "submit_daily_report",
                "approve_workflow_step",
                "dashboard_summary",
                "create_workflow_step",
            ):
                if key in timings:
                    print(f"    {key}: {timings[key]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
