"""Append-only usage event store (JSONL — no analytics domain tables)."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID


def _usage_path() -> Path:
    raw = os.getenv("OPERATIONAL_USAGE_PATH", "data/operational_usage.jsonl").strip()
    path = Path(raw)
    if not path.is_absolute():
        root = Path(__file__).resolve().parents[3]
        path = root / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def append_usage_event(
    *,
    username: str,
    role: str,
    event_type: str,
    page_path: str,
    session_id: str | None,
    referrer_path: str | None,
    project_id: UUID | None,
) -> dict[str, Any]:
    record = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "username": username,
        "role": role,
        "event_type": event_type,
        "page_path": page_path,
        "session_id": session_id,
        "referrer_path": referrer_path,
        "project_id": str(project_id) if project_id else None,
    }
    path = _usage_path()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def load_usage_events() -> list[dict[str, Any]]:
    path = _usage_path()
    if not path.is_file():
        return []
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events
