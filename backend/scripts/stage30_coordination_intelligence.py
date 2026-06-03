#!/usr/bin/env python3
"""Stage 30 — export coordination intelligence JSON for a project."""

from __future__ import annotations

import json
import os
import sys
from uuid import UUID

os.environ.setdefault("SKIP_STARTUP_VALIDATION", "true")


def main() -> int:
    raw = os.getenv("STAGE30_PROJECT_ID", "").strip()
    if not raw:
        print("Set STAGE30_PROJECT_ID to export coordination intelligence.")
        return 0

    project_id = UUID(raw)
    from backend.phase1.analytics.coordination_intelligence_service import (
        build_project_coordination_intelligence,
    )

    db = None
    try:
        from backend.db.session import SessionLocal

        db = SessionLocal()
        payload = build_project_coordination_intelligence(db, project_id)
    except Exception as exc:  # noqa: BLE001
        print(f"DB unavailable ({exc}); degraded coordination payload.")
        payload = build_project_coordination_intelligence(None, project_id)
    finally:
        if db is not None:
            db.close()

    print("Stage 30 coordination intelligence")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
