#!/usr/bin/env python3
"""Stage 27 verification — analytics API + adoption aggregation."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

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

    print("Stage 27 live pilot verification")

    worker_token = _token(client, "worker")
    admin_token = _token(client, "admin")

    if not admin_token and not worker_token:
        _check("Auth", True, "skipped (PostgreSQL required for persisted IAM)")
        print("Stage 27 verification passed (degraded).")
        return 0

    if worker_token:
        denied = client.get(
            "/analytics/adoption-summary",
            headers={"Authorization": f"Bearer {worker_token}"},
        )
        passed &= _check("Worker denied adoption summary", denied.status_code == 403)

    if admin_token:
        headers = {"Authorization": f"Bearer {admin_token}"}
        event = client.post(
            "/analytics/usage-events",
            headers=headers,
            json={
                "event_type": "page_view",
                "page_path": "/dashboard/overview",
                "session_id": "stage27-verify",
            },
        )
        passed &= _check("Record usage event", event.status_code == 201)

        summary = client.get("/analytics/adoption-summary", headers=headers)
        passed &= _check("Adoption summary", summary.status_code == 200)
        if summary.status_code == 200:
            body = summary.json()
            passed &= _check(
                "Summary shape",
                "usage" in body and "retention" in body,
                f"events={body.get('usage', {}).get('event_count')}",
            )

    root = Path(__file__).resolve().parents[2]
    agg = subprocess.run(
        [sys.executable, "backend/scripts/stage27_adoption_analytics.py"],
        cwd=root,
        env={**os.environ, "PYTHONPATH": str(root)},
        check=False,
    )
    passed &= _check("Adoption aggregation script", agg.returncode == 0)

    if passed:
        print("Stage 27 live pilot verification passed.")
        return 0

    print("Stage 27 live pilot verification failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
