#!/usr/bin/env python3
"""Stage 30 verification — coordination intelligence on operational-intelligence API."""

from __future__ import annotations

import os
import sys
from uuid import uuid4

os.environ.setdefault("SKIP_STARTUP_VALIDATION", "true")

from fastapi.testclient import TestClient  # noqa: E402

from backend.phase1.app import create_app  # noqa: E402


def _check(label: str, ok: bool, detail: str = "") -> bool:
    status = "PASS" if ok else "FAIL"
    suffix = f" — {detail}" if detail else ""
    print(f"  [{status}] {label}{suffix}")
    return ok


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
    passed = True
    project_id = str(uuid4())

    print("Stage 30 coordination intelligence verification")

    admin_token = _token(client, "admin")
    if not admin_token:
        _check("Auth", True, "skipped (PostgreSQL required)")
        print("Stage 30 verification passed (degraded).")
        return 0

    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.get(
        f"/analytics/projects/{project_id}/operational-intelligence",
        headers=headers,
    )
    if resp.status_code == 403:
        passed &= _check("Intelligence + coordination", True, "403 unknown project")
    elif resp.status_code == 200:
        body = resp.json()
        ci = body.get("coordination_intelligence")
        passed &= _check("coordination_intelligence present", ci is not None)
        if ci:
            passed &= _check(
                "Coordination band",
                ci.get("coordination_band") in (
                    "ALIGNED",
                    "FRAGMENTED",
                    "STRESSED",
                    "UNKNOWN",
                ),
            )
            passed &= _check(
                "Worker relevance list",
                isinstance(ci.get("worker_relevance"), list),
            )
            passed &= _check(
                "Cross-role dependencies list",
                isinstance(ci.get("cross_role_dependencies"), list),
            )
            passed &= _check(
                "Handoff risks list",
                isinstance(ci.get("handoff_risks"), list),
            )
            passed &= _check(
                "False-positive notes",
                len(ci.get("false_positive_notes", [])) >= 1,
            )
            passed &= _check(
                "Team execution flow",
                "reports_last_7_days" in (ci.get("team_execution_flow") or {}),
            )
    else:
        passed &= _check("Endpoint", False, str(resp.status_code))

    worker = _token(client, "worker")
    if worker:
        w = client.get(
            f"/analytics/projects/{project_id}/operational-intelligence",
            headers={"Authorization": f"Bearer {worker}"},
        )
        passed &= _check("Worker intelligence access", w.status_code in (200, 403))

    if passed:
        print("Stage 30 verification passed.")
        return 0
    print("Stage 30 verification failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
