#!/usr/bin/env python3
"""Stage 22 PostgreSQL runtime validation (requires live Postgres)."""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import date
from uuid import uuid4

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

os.environ.setdefault("SKIP_STARTUP_VALIDATION", "true")

from backend.config import get_settings  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from backend.phase1.app import create_app  # noqa: E402


def main() -> int:
    failures: list[str] = []
    settings = get_settings()
    engine = create_engine(settings.database_url, pool_pre_ping=True)

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            uuid_row = connection.execute(
                text("SELECT gen_random_uuid()::text"),
            ).scalar()
            if not uuid_row or len(uuid_row) != 36:
                failures.append("UUID generation failed")
            connection.execute(
                text("SELECT '{}'::jsonb->>'k'"),
            )
    except SQLAlchemyError as exc:
        print(f"PostgreSQL unavailable: {exc}")
        return 1

    client = TestClient(create_app())
    token = client.post(
        "/auth/token",
        data={"username": "admin", "password": "admin"},
    )
    if token.status_code != 200:
        failures.append(f"login failed: {token.status_code}")
        _report(failures)
        return 1

    headers = {"Authorization": f"Bearer {token.json()['access_token']}"}
    code = f"PG22-{uuid4().hex[:8]}"

    create = client.post(
        "/planning/projects",
        json={"code": code, "name": "PG22 Validation", "status": "ACTIVE"},
        headers=headers,
    )
    if create.status_code != 201:
        failures.append(f"create project: {create.status_code} {create.text}")
        _report(failures)
        return 1

    project_id = create.json()["id"]
    list_resp = client.get(
        f"/runtime/projects/{project_id}/work-orders?limit=5&offset=0",
        headers=headers,
    )
    if list_resp.status_code != 200:
        failures.append(f"work-orders list: {list_resp.status_code}")
    else:
        body = list_resp.json()
        for key in ("items", "total", "limit", "offset"):
            if key not in body:
                failures.append(f"pagination missing {key}")

    # JSONB daily report path
    wo = client.post(
        "/planning/work-orders",
        json={
            "project_id": project_id,
            "work_order_number": f"WO-{uuid4().hex[:6]}",
            "title": "PG22 WO",
            "planned_date": str(date.today()),
        },
        headers=headers,
    )
    if wo.status_code == 201:
        wo_body = wo.json()
        report = client.post(
            "/runtime/daily-reports",
            json={
                "work_order_id": wo_body["id"],
                "report_date": str(date.today()),
                "status": "SUBMITTED",
                "evidence_metadata": {"probe": True, "n": 1},
                "expected_work_order_updated_at": wo_body["updated_at"],
            },
            headers=headers,
        )
        if report.status_code != 201:
            failures.append(f"daily report jsonb: {report.status_code}")

        dup_assign = client.post(
            f"/runtime/work-orders/{wo_body['id']}/assign",
            json={
                "workflow_step_id": "00000000-0000-0000-0000-000000000001",
                "execution_weight": "50",
            },
            headers=headers,
        )
        if dup_assign.status_code not in (201, 404, 409):
            failures.append(f"assign unexpected: {dup_assign.status_code}")

    # Membership: worker should not see unrelated project
    worker_token = client.post(
        "/auth/token",
        data={"username": "worker", "password": "worker"},
    ).json()["access_token"]
    worker_headers = {"Authorization": f"Bearer {worker_token}"}
    denied = client.get(
        f"/runtime/projects/{project_id}/dashboard-summary",
        headers=worker_headers,
    )
    if denied.status_code != 403:
        failures.append(f"worker scoping expected 403 got {denied.status_code}")

    # Pagination timing smoke (no hard SLA)
    start = time.perf_counter()
    client.get("/runtime/projects?limit=50&offset=0", headers=headers)
    elapsed_ms = (time.perf_counter() - start) * 1000
    if elapsed_ms > 5000:
        failures.append(f"list_projects slow: {elapsed_ms:.0f}ms")

    _report(failures)
    return 1 if failures else 0


def _report(failures: list[str]) -> None:
    if failures:
        print("Stage 22 PostgreSQL validation FAILED:")
        for item in failures:
            print(f"  - {item}")
    else:
        print("Stage 22 PostgreSQL validation passed.")


if __name__ == "__main__":
    sys.exit(main())
