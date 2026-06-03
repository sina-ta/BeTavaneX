"""Mirror operational audit entries to JSONL for adoption aggregation."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def _audit_jsonl_path() -> Path:
    raw = os.getenv("OPERATIONAL_AUDIT_JSONL_PATH", "data/operational_audit.jsonl").strip()
    path = Path(raw)
    if not path.is_absolute():
        root = Path(__file__).resolve().parents[3]
        path = root / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def append_audit_record(payload: dict[str, Any]) -> None:
    path = _audit_jsonl_path()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")


def load_audit_records() -> list[dict[str, Any]]:
    path = _audit_jsonl_path()
    if not path.is_file():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records
