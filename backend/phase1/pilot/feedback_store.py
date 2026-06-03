"""Append-only pilot feedback store (JSONL file — no product domain table)."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID


def _feedback_path() -> Path:
    raw = os.getenv("PILOT_FEEDBACK_PATH", "data/pilot_feedback.jsonl").strip()
    path = Path(raw)
    if not path.is_absolute():
        root = Path(__file__).resolve().parents[3]
        path = root / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def append_pilot_feedback(
    *,
    username: str,
    role: str,
    category: str,
    message: str,
    page_path: str | None,
    project_id: UUID | None,
) -> dict[str, Any]:
    record = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "username": username,
        "role": role,
        "category": category,
        "message": message,
        "page_path": page_path,
        "project_id": str(project_id) if project_id else None,
    }
    path = _feedback_path()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record
