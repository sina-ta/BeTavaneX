#!/usr/bin/env python3
"""Print Stage 29 decision support for a project (requires STAGE29_PROJECT_ID + Postgres)."""

from __future__ import annotations

import json
import os
import sys
from uuid import UUID

os.environ.setdefault("SKIP_STARTUP_VALIDATION", "true")


def main() -> int:
    raw = os.getenv("STAGE29_PROJECT_ID", "").strip()
    if not raw:
        print("Set STAGE29_PROJECT_ID to a project UUID.")
        print("Example: STAGE29_PROJECT_ID=... python backend/scripts/stage29_decision_support.py")
        return 1

    project_id = UUID(raw)
    from backend.db.session import SessionLocal
    from backend.phase1.analytics.decision_support_service import (
        build_project_decision_support,
    )

    db = SessionLocal()
    try:
        payload = build_project_decision_support(db, project_id)
    finally:
        db.close()

    print(json.dumps(payload, indent=2, default=str))
    pq = payload.get("priority_queue", [])
    print(f"\nPriority items: {len(pq)} | Recommendations: {len(payload.get('recommendations', []))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
