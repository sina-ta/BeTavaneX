#!/usr/bin/env python3
"""Verify Phase 1 backend routes for frontend runtime wiring."""

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


def main() -> int:
    client = TestClient(create_app(), raise_server_exceptions=False)
    passed = True

    print("Runtime wiring verification (Phase 1 app)")

    passed &= _check("GET /docs", client.get("/docs").status_code == 200)
    passed &= _check("GET /health/live", client.get("/health/live").status_code == 200)
    passed &= _check("GET /openapi.json", client.get("/openapi.json").status_code == 200)

    openapi = client.get("/openapi.json").json()
    paths = openapi.get("paths", {})
    for required in (
        "/auth/token",
        "/planning/projects",
        "/runtime/projects",
        "/analytics/adoption-summary",
    ):
        passed &= _check(f"OpenAPI path {required}", required in paths)

    token = client.post(
        "/auth/token",
        data={"username": "admin", "password": "admin"},
    )
    if token.status_code == 200:
        passed &= _check("POST /auth/token", True)
        headers = {"Authorization": f"Bearer {token.json()['access_token']}"}
        passed &= _check(
            "GET /runtime/projects",
            client.get("/runtime/projects", headers=headers).status_code == 200,
        )
        passed &= _check(
            "GET /analytics/adoption-summary",
            client.get("/analytics/adoption-summary", headers=headers).status_code
            in (200, 403),
        )
    else:
        passed &= _check(
            "POST /auth/token",
            False,
            f"{token.status_code} (PostgreSQL required for persisted IAM)",
        )

    if passed:
        print("\nRuntime wiring verification passed.")
        return 0
    print("\nRuntime wiring verification failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
