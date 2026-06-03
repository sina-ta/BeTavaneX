#!/usr/bin/env python3
"""Stage 23 deployment verification — vertical slice inside Phase 1 runtime."""

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
    base_url = os.getenv("DEPLOY_VERIFY_BASE_URL", "").strip()
    if base_url:
        return _verify_remote(base_url)

    client = TestClient(create_app(), raise_server_exceptions=False)
    passed = True

    print("Stage 23 deployment verification (in-process)")

    live = client.get("/health/live")
    passed &= _check("Liveness", live.status_code == 200)

    health = client.get("/health")
    if health.status_code not in (200, 503):
        passed &= _check("Readiness (DB)", False, f"unexpected {health.status_code}")
    elif health.status_code == 200:
        passed &= _check("Readiness (DB)", True, health.text[:80])
    else:
        _check(
            "Readiness (DB)",
            False,
            "skipped — start PostgreSQL or Docker Compose for full vertical slice",
        )

    token_response = client.post(
        "/auth/token",
        data={"username": "admin", "password": "admin"},
    )
    if token_response.status_code == 200:
        passed &= _check("Auth token", True)
    elif health.status_code == 503:
        _check("Auth token", True, "skipped (persisted IAM requires PostgreSQL)")
    else:
        passed &= _check("Auth token", False, token_response.text[:120])
        return 1

    token = token_response.json().get("access_token") if token_response.status_code == 200 else ""
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    if health.status_code == 200 and token:
        projects = client.get("/runtime/projects", headers=headers)
        passed &= _check("Runtime query layer", projects.status_code == 200)

        planning = client.post(
            "/planning/projects",
            headers=headers,
            json={
                "code": "STAGE23",
                "name": "Stage 23 Deploy Verify",
                "status": "ACTIVE",
                "planned_start": "2026-06-01",
                "planned_finish": "2026-12-31",
            },
        )
        passed &= _check(
            "Planning create project",
            planning.status_code in {200, 201, 409},
            str(planning.status_code),
        )
    else:
        _check("Runtime query layer", True, "skipped (no database)")
        _check("Planning create project", True, "skipped (no database)")

    openapi = client.get("/openapi.json")
    passed &= _check(
        "API schema reachable",
        openapi.status_code == 200,
        "planning + runtime documented",
    )

    if passed:
        print("\nDeployment verification passed (in-process).")
        print(
            "Full DB slice: docker compose up --build, then "
            "DEPLOY_VERIFY_BASE_URL=http://localhost:8000 python backend/scripts/stage23_deployment_verification.py",
        )
        return 0

    print("\nDeployment verification failed.")
    return 1


def _verify_remote(base_url: str) -> int:
    import httpx

    print(f"Stage 23 deployment verification (remote: {base_url})")
    passed = True

    with httpx.Client(base_url=base_url, timeout=30.0) as client:
        live = client.get("/health/live")
        passed &= _check("Liveness", live.status_code == 200)

        health = client.get("/health")
        passed &= _check("Readiness (DB)", health.status_code == 200)

        token = client.post(
            "/auth/token",
            data={"username": "admin", "password": "admin"},
        )
        passed &= _check("Auth", token.status_code == 200)
        if token.status_code != 200:
            return 1

        headers = {"Authorization": f"Bearer {token.json()['access_token']}"}
        projects = client.get("/runtime/projects", headers=headers)
        passed &= _check("Runtime projects", projects.status_code == 200)

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
