#!/usr/bin/env python3
"""Stage 22 operational stress review (audit-only, requires PostgreSQL)."""

from __future__ import annotations

import os
import sys
import time

from sqlalchemy import create_engine, text

os.environ.setdefault("SKIP_STARTUP_VALIDATION", "true")

from backend.config import get_settings  # noqa: E402


def _timed(label: str, connection, statement: str) -> float:
    start = time.perf_counter()
    connection.execute(text(statement))
    elapsed = (time.perf_counter() - start) * 1000
    print(f"  {label}: {elapsed:.1f}ms")
    return elapsed


def main() -> int:
    settings = get_settings()
    engine = create_engine(settings.database_url, pool_pre_ping=True)

    findings: list[str] = []

    try:
        with engine.connect() as connection:
            _timed("SELECT 1", connection, "SELECT 1")
            report_count = connection.execute(
                text("SELECT COUNT(*) FROM daily_reports"),
            ).scalar()
            wo_count = connection.execute(
                text("SELECT COUNT(*) FROM work_orders"),
            ).scalar()
            print(f"  daily_reports rows: {report_count}")
            print(f"  work_orders rows: {wo_count}")

            if report_count and report_count > 10_000:
                findings.append(
                    "Large daily_reports volume: consider date-indexed pagination only",
                )

            elapsed = _timed(
                "projects list filter",
                connection,
                "SELECT id FROM projects ORDER BY created_at DESC LIMIT 200",
            )
            if elapsed > 500:
                findings.append("Project list query >500ms — review indexes")

            _timed(
                "work_orders by project",
                connection,
                """
                SELECT id FROM work_orders
                WHERE project_id IS NOT NULL
                ORDER BY planned_date DESC
                LIMIT 200
                """,
            )
    except Exception as exc:  # noqa: BLE001
        print(f"Stress review skipped: {exc}")
        return 0

    print("\nStress review findings:")
    if not findings:
        print("  None critical at current dataset size.")
    else:
        for item in findings:
            print(f"  - {item}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
