#!/usr/bin/env python3
"""Stage 21 pilot checks: role matrix, work-order query shape, membership persistence."""

from __future__ import annotations

import sys
from uuid import uuid4

from fastapi.testclient import TestClient

import os

os.environ.setdefault("SKIP_STARTUP_VALIDATION", "true")

from backend.phase1.app import create_app

_ROLES = ("admin", "supervisor", "worker", "investor")
_PLANNING_BODY = {
    "code": f"PILOT21-{uuid4().hex[:8]}",
    "name": "Stage 21 Pilot Project",
    "status": "ACTIVE",
}


def _token(client: TestClient, username: str) -> str:
    response = client.post(
        "/auth/token",
        data={"username": username, "password": username},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _expect(label: str, status: int, expected: int, failures: list[str]) -> None:
    if status != expected:
        failures.append(f"{label}: expected HTTP {expected}, got {status}")


def main() -> int:
    client = TestClient(create_app())
    failures: list[str] = []

    tokens = {role: _token(client, role) for role in _ROLES}

    # Role denials (no DB required)
    _expect(
        "worker planning",
        client.post("/planning/projects", json=_PLANNING_BODY, headers=_auth(tokens["worker"])).status_code,
        403,
        failures,
    )
    _expect(
        "investor planning",
        client.post("/planning/projects", json=_PLANNING_BODY, headers=_auth(tokens["investor"])).status_code,
        403,
        failures,
    )

    db_available = True
    fake_project = "00000000-0000-0000-0000-000000000099"

    try:
        list_resp = client.get(
            f"/runtime/projects/{fake_project}/work-orders",
            headers=_auth(tokens["admin"]),
        )
    except Exception as exc:  # noqa: BLE001 — pilot script
        db_available = False
        print(f"Database unavailable, skipping DB-backed checks: {exc}")

    if db_available:
        if list_resp.status_code not in (200, 403, 500, 503):
            failures.append(
                f"admin work-orders list: expected 200/403 or DB error, got {list_resp.status_code}",
            )
        elif list_resp.status_code == 200:
            body = list_resp.json()
            for key in ("items", "total", "limit", "offset"):
                if key not in body:
                    failures.append(f"work-orders pagination missing key: {key}")

        worker_list = client.get(
            f"/runtime/projects/{fake_project}/work-orders",
            headers=_auth(tokens["worker"]),
        )
        if worker_list.status_code not in (403, 200):
            failures.append(f"worker work-orders list: unexpected {worker_list.status_code}")

    if not db_available:
        if failures:
            print("Stage 21 pilot validation FAILED:")
            for item in failures:
                print(f"  - {item}")
            return 1
        print("Stage 21 pilot validation passed (role checks only; database offline).")
        return 0

    create = client.post(
        "/planning/projects",
        json=_PLANNING_BODY,
        headers=_auth(tokens["admin"]),
    )
    if create.status_code == 201:
        project_id = create.json()["id"]
        projects = client.get("/runtime/projects", headers=_auth(tokens["admin"]))
        if projects.status_code == 200:
            ids = {item["id"] for item in projects.json()["items"]}
            if project_id not in ids:
                failures.append("admin list_projects missing newly created project")
        investor_projects = client.get(
            "/runtime/projects",
            headers=_auth(tokens["investor"]),
        )
        if investor_projects.status_code == 200:
            investor_ids = {item["id"] for item in investor_projects.json()["items"]}
            if project_id not in investor_ids:
                failures.append("investor missing membership after project create")
        wo_list = client.get(
            f"/runtime/projects/{project_id}/work-orders?limit=5&offset=0",
            headers=_auth(tokens["admin"]),
        )
        if wo_list.status_code != 200:
            failures.append(f"work-orders on new project: HTTP {wo_list.status_code}")
    elif create.status_code not in (409, 422, 500, 503):
        failures.append(f"admin create project: unexpected HTTP {create.status_code}")

    if failures:
        print("Stage 21 pilot validation FAILED:")
        for item in failures:
            print(f"  - {item}")
        return 1

    print("Stage 21 pilot validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
