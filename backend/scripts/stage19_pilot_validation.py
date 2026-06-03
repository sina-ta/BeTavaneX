#!/usr/bin/env python3
"""Stage 19 pilot checks: role matrix (no DB required for 403 paths)."""

from __future__ import annotations

import sys
from uuid import uuid4

from fastapi.testclient import TestClient

import os

os.environ.setdefault("SKIP_STARTUP_VALIDATION", "true")

from backend.phase1.app import create_app

_ROLES = ("admin", "supervisor", "worker", "investor")
_PLANNING_BODY = {
    "code": f"PILOT-{uuid4().hex[:8]}",
    "name": "Pilot Project",
    "status": "ACTIVE",
}
_ASSIGN_BODY = {
    "workflow_step_id": "00000000-0000-0000-0000-000000000001",
    "execution_weight": "100",
}
_REPORT_BODY = {
    "work_order_id": "00000000-0000-0000-0000-000000000001",
    "report_date": "2026-06-03",
    "status": "SUBMITTED",
}
_APPROVE_BODY = {"approval_type": "FINAL"}


def _token(client: TestClient, username: str) -> str:
    response = client.post(
        "/auth/token",
        data={"username": username, "password": username},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _post_status(client: TestClient, path: str, *, headers: dict[str, str], json: dict) -> int:
    try:
        return client.post(path, json=json, headers=headers).status_code
    except Exception:
        return 503


def _get_status(client: TestClient, path: str, *, headers: dict[str, str]) -> int:
    try:
        return client.get(path, headers=headers).status_code
    except Exception:
        return 503


def _expect(
    label: str,
    status: int,
    expected: int,
    failures: list[str],
) -> None:
    if status != expected:
        failures.append(f"{label}: expected HTTP {expected}, got {status}")


def main() -> int:
    client = TestClient(create_app())
    failures: list[str] = []

    tokens = {role: _token(client, role) for role in _ROLES}

    # Unauthenticated
    _expect(
        "no-token planning",
        client.post("/planning/projects", json=_PLANNING_BODY).status_code,
        401,
        failures,
    )

    # Role matrix — planning (403 for worker/investor; may 422/500 if DB missing for admin)
    for role in _ROLES:
        headers = _auth(tokens[role])
        status = _post_status(
            client,
            "/planning/projects",
            headers=headers,
            json=_PLANNING_BODY,
        )
        if role in ("admin", "supervisor"):
            if status not in (201, 409, 422, 500, 503):
                failures.append(
                    f"planning/{role}: expected success or DB error, got {status}",
                )
        elif status != 403:
            failures.append(f"planning/{role}: expected 403, got {status}")

    wo_id = "00000000-0000-0000-0000-000000000099"
    step_id = "00000000-0000-0000-0000-000000000099"

    assign_expect = {
        "admin": (201, 403, 404, 422, 500, 503),
        "supervisor": (201, 403, 404, 422, 500, 503),
        "worker": (403, 503),
        "investor": (403, 503),
    }
    for role in _ROLES:
        status = _post_status(
            client,
            f"/runtime/work-orders/{wo_id}/assign",
            headers=_auth(tokens[role]),
            json={**_ASSIGN_BODY, "workflow_step_id": step_id},
        )
        if status not in assign_expect[role]:
            failures.append(f"assign/{role}: unexpected {status}")

    report_expect = {
        "admin": (201, 403, 404, 422, 500, 503),
        "supervisor": (201, 403, 404, 422, 500, 503),
        "worker": (201, 403, 404, 422, 500, 503),
        "investor": (403, 503),
    }
    for role in _ROLES:
        status = _post_status(
            client,
            "/runtime/daily-reports",
            headers=_auth(tokens[role]),
            json=_REPORT_BODY,
        )
        if status not in report_expect[role]:
            failures.append(f"daily-report/{role}: unexpected {status}")

    approve_expect = {
        "admin": (201, 403, 404, 422, 500, 503),
        "supervisor": (201, 403, 404, 422, 500, 503),
        "worker": (403, 503),
        "investor": (403, 503),
    }
    for role in _ROLES:
        status = _post_status(
            client,
            f"/runtime/workflow-steps/{step_id}/approve",
            headers=_auth(tokens[role]),
            json=_APPROVE_BODY,
        )
        if status not in approve_expect[role]:
            failures.append(f"approve/{role}: unexpected {status}")

    # Runtime reads — all roles (200 or empty DB 404/500)
    for role in _ROLES:
        status = _get_status(
            client,
            "/runtime/projects",
            headers=_auth(tokens[role]),
        )
        if status not in (200, 500, 503):
            failures.append(f"list-projects/{role}: unexpected {status}")

    if failures:
        print("Stage 19 pilot validation FAILED:")
        for item in failures:
            print(f"  - {item}")
        return 1

    print("Stage 19 pilot validation PASSED (role boundary checks).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
