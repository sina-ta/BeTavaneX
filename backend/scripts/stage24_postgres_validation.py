#!/usr/bin/env python3
"""Stage 24 PostgreSQL E2E: batch dashboard queries + multi-user scoping."""

from __future__ import annotations

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
    except SQLAlchemyError as exc:
        print(f"PostgreSQL unavailable: {exc}")
        return 1

    client = TestClient(create_app())
    admin_token = client.post(
        "/auth/token",
        data={"username": "admin", "password": "admin"},
    )
    if admin_token.status_code != 200:
        failures.append(f"admin login: {admin_token.status_code}")
        _report(failures)
        return 1

    headers = {"Authorization": f"Bearer {admin_token.json()['access_token']}"}
    code = f"S24-{uuid4().hex[:8]}"

    create = client.post(
        "/planning/projects",
        json={"code": code, "name": "Stage 24 Batch", "status": "ACTIVE"},
        headers=headers,
    )
    if create.status_code != 201:
        failures.append(f"create project: {create.status_code} {create.text}")
        _report(failures)
        return 1

    project_id = create.json()["id"]

    start = time.perf_counter()
    batch = client.get(
        f"/runtime/projects/{project_id}/workflow-steps-batch?limit=500&offset=0",
        headers=headers,
    )
    batch_ms = (time.perf_counter() - start) * 1000
    if batch.status_code != 200:
        failures.append(f"workflow-steps-batch: {batch.status_code}")
    else:
        body = batch.json()
        for key in ("items", "total", "limit", "offset"):
            if key not in body:
                failures.append(f"batch pagination missing {key}")
        if batch_ms > 10_000:
            failures.append(f"batch query slow: {batch_ms:.0f}ms")

    summary = client.get(
        f"/runtime/projects/{project_id}/dashboard-summary",
        headers=headers,
    )
    if summary.status_code != 200:
        failures.append(f"dashboard-summary: {summary.status_code}")

    wo = client.post(
        "/planning/work-orders",
        json={
            "project_id": project_id,
            "work_order_number": f"WO-{uuid4().hex[:6]}",
            "title": "S24 WO",
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
                "expected_work_order_updated_at": wo_body["updated_at"],
            },
            headers=headers,
        )
        if report.status_code != 201:
            failures.append(f"daily report: {report.status_code}")

    worker_headers = {
        "Authorization": f"Bearer {client.post('/auth/token', data={'username': 'worker', 'password': 'worker'}).json()['access_token']}",
    }
    denied = client.get(
        f"/runtime/projects/{project_id}/workflow-steps-batch",
        headers=worker_headers,
    )
    if denied.status_code != 403:
        failures.append(f"worker batch scoping expected 403 got {denied.status_code}")

    investor_headers = {
        "Authorization": f"Bearer {client.post('/auth/token', data={'username': 'investor', 'password': 'investor'}).json()['access_token']}",
    }
    inv_batch = client.get(
        f"/runtime/projects/{project_id}/workflow-steps-batch",
        headers=investor_headers,
    )
    if inv_batch.status_code not in (200, 403):
        failures.append(f"investor batch unexpected {inv_batch.status_code}")

    _report(failures)
    return 1 if failures else 0


def _report(failures: list[str]) -> None:
    if failures:
        print("Stage 24 PostgreSQL validation FAILED:")
        for item in failures:
            print(f"  - {item}")
    else:
        print("Stage 24 PostgreSQL validation passed.")


if __name__ == "__main__":
    sys.exit(main())
