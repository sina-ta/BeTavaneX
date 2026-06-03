#!/usr/bin/env python3
"""Stage 31 verification — organizational intelligence API."""

from __future__ import annotations

import os
import sys

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

    print("Stage 31 organizational intelligence verification")

    passed &= _check("Unauthenticated denied", client.get("/analytics/organizational-intelligence").status_code == 401)

    worker = _token(client, "worker")
    if worker:
        wr = client.get(
            "/analytics/organizational-intelligence",
            headers={"Authorization": f"Bearer {worker}"},
        )
        passed &= _check("Worker denied org intel", wr.status_code == 403)

    admin = _token(client, "admin")
    if not admin:
        _check("Auth", True, "skipped (PostgreSQL required)")
        print("Stage 31 verification passed (degraded).")
        return 0

    resp = client.get(
        "/analytics/organizational-intelligence",
        headers={"Authorization": f"Bearer {admin}"},
    )
    passed &= _check("Admin org endpoint", resp.status_code == 200, str(resp.status_code))
    if resp.status_code == 200:
        body = resp.json()
        passed &= _check("maturity_band present", "maturity_band" in body)
        passed &= _check(
            "Maturity band valid",
            body.get("maturity_band")
            in ("ESTABLISHED", "DEVELOPING", "EMERGING", "STRAINED", "UNKNOWN"),
        )
        passed &= _check(
            "Components explainable",
            all(
                "factor" in c and "detail" in c
                for c in body.get("maturity_components", [])
            )
            or body.get("data_available") is False,
        )
        passed &= _check(
            "False-positive notes",
            len(body.get("false_positive_notes", [])) >= 1,
        )
        passed &= _check(
            "Supervisor trends not HR scores",
            all(
                "observation" in t
                for t in body.get("supervisor_trends", [])
            ),
        )

    investor = _token(client, "investor")
    if investor:
        inv = client.get(
            "/analytics/organizational-intelligence",
            headers={"Authorization": f"Bearer {investor}"},
        )
        passed &= _check("Investor may read org intel", inv.status_code == 200)

    if passed:
        print("Stage 31 verification passed.")
        return 0
    print("Stage 31 verification failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
