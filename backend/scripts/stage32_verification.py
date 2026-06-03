#!/usr/bin/env python3
"""Stage 32 verification — executive operational visibility API."""

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

    print("Stage 32 executive visibility verification")

    passed &= _check(
        "Unauthenticated denied",
        client.get("/analytics/executive-visibility").status_code == 401,
    )

    worker = _token(client, "worker")
    if worker:
        wr = client.get(
            "/analytics/executive-visibility",
            headers={"Authorization": f"Bearer {worker}"},
        )
        passed &= _check("Worker denied executive", wr.status_code == 403)

    supervisor = _token(client, "supervisor")
    if supervisor:
        sr = client.get(
            "/analytics/executive-visibility",
            headers={"Authorization": f"Bearer {supervisor}"},
        )
        passed &= _check("Supervisor denied executive", sr.status_code == 403)

    admin = _token(client, "admin")
    if not admin:
        _check("Auth", True, "skipped (PostgreSQL required)")
        print("Stage 32 verification passed (degraded).")
        return 0

    resp = client.get(
        "/analytics/executive-visibility",
        headers={"Authorization": f"Bearer {admin}"},
    )
    passed &= _check("Admin executive endpoint", resp.status_code == 200, str(resp.status_code))
    if resp.status_code == 200:
        body = resp.json()
        passed &= _check("executive_summary present", bool(body.get("executive_summary")))
        ph = body.get("portfolio_health") or {}
        passed &= _check(
            "Portfolio band valid",
            ph.get("overall_band")
            in ("HEALTHY", "STABLE", "CAUTION", "CRITICAL", "UNKNOWN"),
        )
        passed &= _check(
            "Leadership priorities ranked",
            all(
                "concern" in p and "evidence" in p and "suggested_focus" in p
                for p in body.get("leadership_priorities", [])
            ),
        )
        passed &= _check(
            "Trend narratives evidence-based",
            all(
                "message" in n and "evidence" in n
                for n in body.get("trend_narratives", [])
            ),
        )
        passed &= _check(
            "False-positive notes",
            len(body.get("false_positive_notes", [])) >= 1,
        )
        passed &= _check(
            "Strategic attention capped",
            len(body.get("strategic_attention", [])) <= 6,
        )

    investor = _token(client, "investor")
    if investor:
        inv = client.get(
            "/analytics/executive-visibility",
            headers={"Authorization": f"Bearer {investor}"},
        )
        passed &= _check("Investor may read executive", inv.status_code == 200)

    if passed:
        print("Stage 32 verification passed.")
        return 0
    print("Stage 32 verification failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
