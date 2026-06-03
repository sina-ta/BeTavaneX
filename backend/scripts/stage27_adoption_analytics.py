#!/usr/bin/env python3
"""Stage 27 — print adoption summary from JSONL (+ optional Postgres snapshot)."""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path


def _load_pilot_feedback() -> list[dict]:
    raw = os.getenv("PILOT_FEEDBACK_PATH", "data/pilot_feedback.jsonl").strip()
    path = Path(raw)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[2] / path
    if not path.is_file():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def main() -> int:
    os.environ.setdefault("SKIP_STARTUP_VALIDATION", "true")

    from backend.phase1.analytics.adoption_service import build_adoption_summary

    db = None
    try:
        from backend.db.session import SessionLocal

        db = SessionLocal()
        summary = build_adoption_summary(db)
    except Exception:
        summary = build_adoption_summary(None)
    finally:
        if db is not None:
            db.close()

    print("Stage 27 adoption analytics")
    print(json.dumps(summary, indent=2))

    feedback = _load_pilot_feedback()
    if feedback:
        categories = Counter(row.get("category", "other") for row in feedback)
        print("\nPilot feedback categories:")
        for key, count in categories.most_common():
            print(f"  {key}: {count}")

    if summary["usage"]["event_count"] == 0 and summary["mutations"]["audit_record_count"] == 0:
        print(
            "\nNote: No JSONL events yet. Run live pilot with dashboard usage "
            "or POST /analytics/usage-events.",
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
