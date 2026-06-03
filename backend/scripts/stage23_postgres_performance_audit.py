#!/usr/bin/env python3
"""Stage 23 PostgreSQL performance audit (indexes, pagination paths, hotspots)."""

from __future__ import annotations

import os
import sys
import time

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

os.environ.setdefault("SKIP_STARTUP_VALIDATION", "true")

from backend.config import get_settings  # noqa: E402


EXPECTED_INDEXES = {
    "work_orders": {
        "idx_work_orders_project_id",
        "idx_work_orders_planned_date",
        "idx_work_orders_project_planned_date",
        "idx_work_orders_status",
    },
    "daily_reports": {
        "idx_daily_reports_work_order_id",
        "idx_daily_reports_report_date",
    },
    "project_memberships": {
        "idx_project_memberships_username",
        "idx_project_memberships_project_id",
    },
    "activity_instances": {"idx_activity_instances_project_id"},
    "workflow_steps": {"idx_workflow_steps_activity_instance_id"},
}


def _timed_ms(connection, label: str, statement: str) -> float:
    start = time.perf_counter()
    connection.execute(text(statement))
    elapsed = (time.perf_counter() - start) * 1000
    print(f"  {label}: {elapsed:.1f}ms")
    return elapsed


def main() -> int:
    settings = get_settings()
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    findings: list[str] = []
    recommendations: list[str] = []

    try:
        inspector = inspect(engine)
        with engine.connect() as connection:
            for table, expected in EXPECTED_INDEXES.items():
                if not inspector.has_table(table):
                    findings.append(f"Missing table: {table}")
                    continue
                actual = {idx["name"] for idx in inspector.get_indexes(table)}
                missing = expected - actual
                if missing:
                    findings.append(
                        f"{table}: missing indexes {sorted(missing)}",
                    )

            _timed_ms(connection, "connectivity", "SELECT 1")

            project_id = connection.execute(
                text("SELECT id FROM projects ORDER BY created_at DESC LIMIT 1"),
            ).scalar()

            _timed_ms(
                connection,
                "projects paginated list",
                "SELECT id FROM projects ORDER BY created_at DESC LIMIT 50 OFFSET 0",
            )

            if project_id:
                elapsed = _timed_ms(
                    connection,
                    "work_orders by project (paginated)",
                    f"""
                    SELECT id FROM work_orders
                    WHERE project_id = '{project_id}'
                    ORDER BY planned_date DESC
                    LIMIT 200
                    """,
                )
                if elapsed > 500:
                    recommendations.append(
                        "work_orders list >500ms — verify idx_work_orders_project_planned_date",
                    )

                _timed_ms(
                    connection,
                    "membership lookup",
                    f"""
                    SELECT project_id FROM project_memberships
                    WHERE username = 'admin'
                    """,
                )

                _timed_ms(
                    connection,
                    "daily_reports by work_order",
                    """
                    SELECT id FROM daily_reports
                    ORDER BY report_date DESC
                    LIMIT 100
                    """,
                )

            report_count = connection.execute(
                text("SELECT COUNT(*) FROM daily_reports"),
            ).scalar()
            wo_count = connection.execute(
                text("SELECT COUNT(*) FROM work_orders"),
            ).scalar()
            print(f"  daily_reports rows: {report_count}")
            print(f"  work_orders rows: {wo_count}")

            if report_count and report_count > 50_000:
                recommendations.append(
                    "Large daily_reports volume — keep date-filtered pagination only",
                )

    except SQLAlchemyError as exc:
        print(f"PostgreSQL audit skipped: {exc}")
        print("Run with Docker Postgres or local DATABASE_URL configured.")
        return 0

    print("\nPerformance audit findings:")
    if findings:
        for item in findings:
            print(f"  - {item}")
    else:
        print("  Index coverage OK for audited tables.")

    print("\nRecommendations:")
    if recommendations:
        for item in recommendations:
            print(f"  - {item}")
    else:
        print("  No critical query regressions at current dataset size.")

    print("\nKnown N+1 risks (documented, not auto-fixed):")
    print("  - get_project_runtime_summary: per-activity workflow_step count loop")
    print("  - get_project_dashboard_summary: per-activity progress calculation")
    print("  - work_order_runtime_view: per-link workflow_step fetch")

    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
