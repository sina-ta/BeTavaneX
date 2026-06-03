#!/usr/bin/env python3
"""Stage 28 — export explainable operational intelligence for a project."""

from __future__ import annotations

import json
import os
import sys
from uuid import UUID

os.environ.setdefault("SKIP_STARTUP_VALIDATION", "true")


def main() -> int:
    raw = os.getenv("STAGE28_PROJECT_ID", "").strip()
    if not raw:
        print("Set STAGE28_PROJECT_ID to a project UUID (or pass via env in CI).")
        print("Example: STAGE28_PROJECT_ID=... python backend/scripts/stage28_operational_intelligence.py")
        return 0

    project_id = UUID(raw)
    from backend.phase1.analytics.operational_intelligence_service import (
        build_project_operational_intelligence,
    )

    db = None
    try:
        from backend.db.session import SessionLocal

        db = SessionLocal()
        payload = build_project_operational_intelligence(db, project_id)
    except Exception as exc:  # noqa: BLE001
        print(f"DB unavailable ({exc}); JSONL-only signals.")
        payload = build_project_operational_intelligence(None, project_id)
    finally:
        if db is not None:
            db.close()

    print("Stage 28 operational intelligence")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
