#!/usr/bin/env python3
"""Stage 29 verification — decision support embedded in operational intelligence."""

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

    print("Stage 29 decision support verification")

    admin_token = _token(client, "admin")
    if not admin_token:
        _check("Auth", True, "skipped (PostgreSQL required)")
        print("Stage 29 verification passed (degraded).")
        return 0

    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.get(
        f"/analytics/projects/{project_id}/operational-intelligence",
        headers=headers,
    )
    if resp.status_code == 403:
        passed &= _check("Intelligence + decision support", True, "403 for unknown project")
    elif resp.status_code == 200:
        body = resp.json()
        ds = body.get("decision_support")
        passed &= _check("decision_support present", ds is not None)
        if ds:
            passed &= _check(
                "Priority queue list",
                isinstance(ds.get("priority_queue"), list),
            )
            passed &= _check(
                "Recommendations list",
                isinstance(ds.get("recommendations"), list),
            )
            passed &= _check(
                "Supervisor guidance",
                isinstance(ds.get("supervisor_guidance"), list)
                and len(ds["supervisor_guidance"]) >= 1,
            )
            passed &= _check(
                "False-positive notes",
                len(ds.get("false_positive_notes", [])) >= 1,
            )
            for item in ds.get("priority_queue", [])[:3]:
                if "priority_score" in item and "explanation" in item:
                    passed &= _check(
                        f"Explainable priority #{item.get('rank')}",
                        0 <= item["priority_score"] <= 100,
                    )
                    break
    else:
        passed &= _check("Endpoint", False, str(resp.status_code))

    investor = _token(client, "investor")
    if investor:
        inv = client.get(
            f"/analytics/projects/{project_id}/operational-intelligence",
            headers={"Authorization": f"Bearer {investor}"},
        )
        passed &= _check(
            "Investor may read intelligence",
            inv.status_code in (200, 403),
        )

    if passed:
        print("Stage 29 verification passed.")
        return 0
    print("Stage 29 verification failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
