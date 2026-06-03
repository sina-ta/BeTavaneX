#!/usr/bin/env python3
"""Stage 25 controlled pilot — timed operational vertical slice + pilot metrics JSON."""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import date
from typing import Any
from uuid import uuid4

os.environ.setdefault("SKIP_STARTUP_VALIDATION", "true")

from fastapi.testclient import TestClient  # noqa: E402

from backend.phase1.app import create_app  # noqa: E402

_ROLES = ("admin", "supervisor", "worker", "investor")


def _timed(label: str, fn) -> tuple[Any, float, int]:
    start = time.perf_counter()
    response = fn()
    elapsed_ms = (time.perf_counter() - start) * 1000
    status = getattr(response, "status_code", 0)
    return response, elapsed_ms, status


def _token(client: TestClient, username: str) -> str | None:
    response = client.post(
        "/auth/token",
        data={"username": username, "password": username},
    )
    if response.status_code != 200:
        return None
    return response.json()["access_token"]


def main() -> int:
    client = TestClient(create_app(), raise_server_exceptions=False)
    metrics: dict[str, Any] = {
        "stage": 25,
        "database_available": False,
        "timings_ms": {},
        "http_status": {},
        "conflicts": 0,
        "errors": [],
    }

    health = client.get("/health")
    metrics["http_status"]["health"] = health.status_code
    if health.status_code not in (200, 503):
        metrics["errors"].append(f"unexpected health: {health.status_code}")
        _emit(metrics)
        return 1

    metrics["database_available"] = health.status_code == 200

    for role in _ROLES:
        _, ms, status = _timed(
            f"login_{role}",
            lambda r=role: client.post(
                "/auth/token",
                data={"username": r, "password": r},
            ),
        )
        metrics["timings_ms"][f"login_{role}"] = round(ms, 2)
        metrics["http_status"][f"login_{role}"] = status

    if not metrics["database_available"]:
        print("Stage 25 pilot simulation: role logins only (PostgreSQL offline).")
        _emit(metrics)
        return 0

    admin_token = _token(client, "admin")
    if not admin_token:
        metrics["errors"].append("admin login failed")
        _emit(metrics)
        return 1

    headers = {"Authorization": f"Bearer {admin_token}"}
    code = f"PILOT25-{uuid4().hex[:8]}"

    create, ms, status = _timed(
        "create_project",
        lambda: client.post(
            "/planning/projects",
            json={
                "code": code,
                "name": "Stage 25 Pilot",
                "status": "ACTIVE",
                "planned_start": "2026-06-01",
                "planned_finish": "2026-12-31",
            },
            headers=headers,
        ),
    )
    metrics["timings_ms"]["create_project"] = round(ms, 2)
    metrics["http_status"]["create_project"] = status
    if status != 201:
        metrics["errors"].append(f"create_project: {status}")
        _emit(metrics)
        return 1

    project_id = create.json()["id"]

    wbs, ms, status = _timed(
        "create_wbs",
        lambda: client.post(
            "/planning/wbs-items",
            json={
                "project_id": project_id,
                "code": "WBS-1",
                "name": "Pilot WBS",
                "level": 1,
            },
            headers=headers,
        ),
    )
    metrics["timings_ms"]["create_wbs"] = round(ms, 2)
    metrics["http_status"]["create_wbs"] = status

    loc, ms, status = _timed(
        "create_location",
        lambda: client.post(
            "/planning/locations",
            json={
                "project_id": project_id,
                "code": "LOC-1",
                "name": "Site A",
            },
            headers=headers,
        ),
    )
    metrics["timings_ms"]["create_location"] = round(ms, 2)
    metrics["http_status"]["create_location"] = status

    wbs_id = wbs.json()["id"] if status == 201 else None
    loc_id = loc.json()["id"] if status == 201 else None

    activity, ms, status = _timed(
        "create_activity",
        lambda: client.post(
            "/planning/activity-instances",
            json={
                "project_id": project_id,
                "wbs_item_id": wbs_id,
                "location_id": loc_id,
                "name": "Pilot Activity",
                "status": "IN_PROGRESS",
            },
            headers=headers,
        ),
    )
    metrics["timings_ms"]["create_activity"] = round(ms, 2)
    metrics["http_status"]["create_activity"] = status

    activity_id = activity.json()["id"] if status == 201 else None

    step, ms, status = _timed(
        "create_workflow_step",
        lambda: client.post(
            "/planning/workflow-steps",
            json={
                "activity_instance_id": activity_id,
                "step_number": 1,
                "name": "Pour concrete",
                "status": "PENDING",
                "planned_quantity": "10",
                "unit": "m3",
            },
            headers=headers,
        ),
    )
    metrics["timings_ms"]["create_workflow_step"] = round(ms, 2)
    metrics["http_status"]["create_workflow_step"] = status

    step_id = step.json()["id"] if status == 201 else None

    wo, ms, status = _timed(
        "create_work_order",
        lambda: client.post(
            "/planning/work-orders",
            json={
                "project_id": project_id,
                "work_order_number": f"WO-{uuid4().hex[:6]}",
                "title": "Pilot WO",
                "planned_date": str(date.today()),
            },
            headers=headers,
        ),
    )
    metrics["timings_ms"]["create_work_order"] = round(ms, 2)
    metrics["http_status"]["create_work_order"] = status

    wo_id = wo.json()["id"] if status == 201 else None
    wo_updated = wo.json().get("updated_at") if status == 201 else None

    if wo_id and step_id:
        assign, ms, status = _timed(
            "assign_work_order",
            lambda: client.post(
                f"/runtime/work-orders/{wo_id}/assign",
                json={
                    "workflow_step_id": step_id,
                    "execution_weight": "100",
                },
                headers=headers,
            ),
        )
        metrics["timings_ms"]["assign_work_order"] = round(ms, 2)
        metrics["http_status"]["assign_work_order"] = status

    worker_token = _token(client, "worker")
    if worker_token and wo_id:
        worker_headers = {"Authorization": f"Bearer {worker_token}"}
        report, ms, status = _timed(
            "submit_daily_report",
            lambda: client.post(
                "/runtime/daily-reports",
                json={
                    "work_order_id": wo_id,
                    "report_date": str(date.today()),
                    "status": "SUBMITTED",
                    "evidence_metadata": {"pilot": True},
                    "expected_work_order_updated_at": wo_updated,
                },
                headers=worker_headers,
            ),
        )
        metrics["timings_ms"]["submit_daily_report"] = round(ms, 2)
        metrics["http_status"]["submit_daily_report"] = status

    supervisor_token = _token(client, "supervisor")
    if supervisor_token and step_id:
        sup_headers = {"Authorization": f"Bearer {supervisor_token}"}
        step_get = (
            client.get(
                f"/runtime/activity-instances/{activity_id}/workflow-steps",
                headers=headers,
            )
            if activity_id
            else None
        )
        expected_step_updated = None
        if step_get and step_get.status_code == 200:
            items = step_get.json().get("items", [])
            for item in items:
                if item.get("id") == step_id:
                    expected_step_updated = item.get("updated_at")
                    break

        approve, ms, status = _timed(
            "approve_workflow_step",
            lambda: client.post(
                f"/runtime/workflow-steps/{step_id}/approve",
                json={
                    "approval_status": "APPROVED",
                    "comments": "Pilot approval",
                    "expected_workflow_step_updated_at": expected_step_updated,
                },
                headers=sup_headers,
            ),
        )
        metrics["timings_ms"]["approve_workflow_step"] = round(ms, 2)
        metrics["http_status"]["approve_workflow_step"] = status

        if status == 409:
            metrics["conflicts"] += 1

    dash, ms, status = _timed(
        "dashboard_summary",
        lambda: client.get(
            f"/runtime/projects/{project_id}/dashboard-summary",
            headers=headers,
        ),
    )
    metrics["timings_ms"]["dashboard_summary"] = round(ms, 2)
    metrics["http_status"]["dashboard_summary"] = status

    batch, ms, status = _timed(
        "workflow_steps_batch",
        lambda: client.get(
            f"/runtime/projects/{project_id}/workflow-steps-batch?limit=50",
            headers=headers,
        ),
    )
    metrics["timings_ms"]["workflow_steps_batch"] = round(ms, 2)
    metrics["http_status"]["workflow_steps_batch"] = status

    feedback, ms, status = _timed(
        "pilot_feedback",
        lambda: client.post(
            "/pilot/feedback",
            json={
                "category": "gap",
                "message": "Automated Stage 25 probe feedback",
                "page_path": "/scripts/stage25",
                "project_id": project_id,
            },
            headers=headers,
        ),
    )
    metrics["timings_ms"]["pilot_feedback"] = round(ms, 2)
    metrics["http_status"]["pilot_feedback"] = status

    investor_token = _token(client, "investor")
    if investor_token:
        inv_headers = {"Authorization": f"Bearer {investor_token}"}
        inv_dash, ms, status = _timed(
            "investor_dashboard",
            lambda: client.get(
                f"/runtime/projects/{project_id}/dashboard-summary",
                headers=inv_headers,
            ),
        )
        metrics["timings_ms"]["investor_dashboard"] = round(ms, 2)
        metrics["http_status"]["investor_dashboard"] = status

    failed = [k for k, v in metrics["http_status"].items() if v >= 500]
    if failed:
        metrics["errors"].extend([f"server error on {k}" for k in failed])

    _emit(metrics)
    return 1 if metrics["errors"] else 0


def _emit(metrics: dict[str, Any]) -> None:
    out_path = os.getenv("STAGE25_METRICS_PATH", "").strip()
    payload = json.dumps(metrics, indent=2)
    if out_path:
        with open(out_path, "w", encoding="utf-8") as handle:
            handle.write(payload)
    print(payload)


if __name__ == "__main__":
    sys.exit(main())
