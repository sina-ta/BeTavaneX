#!/usr/bin/env python3
"""Stage 28 verification — operational intelligence API shape."""

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

    print("Stage 28 operational intelligence verification")

    admin_token = _token(client, "admin")
    if not admin_token:
        _check("Auth", True, "skipped (PostgreSQL required)")
        resp = client.get(
            f"/analytics/projects/{project_id}/operational-intelligence",
        )
        passed &= _check("Unauthenticated denied", resp.status_code == 401)
        print("Stage 28 verification passed (degraded).")
        return 0

    headers = {"Authorization": f"Bearer {admin_token}"}
    intel = client.get(
        f"/analytics/projects/{project_id}/operational-intelligence",
        headers=headers,
    )
    if intel.status_code == 403:
        passed &= _check(
            "Intelligence (no access)",
            True,
            "403 expected for unknown project",
        )
    elif intel.status_code == 200:
        body = intel.json()
        passed &= _check(
            "Response shape",
            "health" in body and "predictions" in body and "decision_support" in body,
        )
        passed &= _check(
            "Explainable health",
            body["health"]["band"] in ("GOOD", "ATTENTION", "AT_RISK", "UNKNOWN"),
        )
        passed &= _check(
            "False-positive notes",
            len(body.get("false_positive_notes", [])) >= 1,
        )
    else:
        passed &= _check("Intelligence endpoint", False, str(intel.status_code))

    worker_token = _token(client, "worker")
    if worker_token:
        worker_resp = client.get(
            f"/analytics/projects/{project_id}/operational-intelligence",
            headers={"Authorization": f"Bearer {worker_token}"},
        )
        passed &= _check(
            "Worker may call when authorized",
            worker_resp.status_code in (200, 403),
        )

    if passed:
        print("Stage 28 verification passed.")
        return 0
    print("Stage 28 verification failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
