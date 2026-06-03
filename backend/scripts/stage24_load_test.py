#!/usr/bin/env python3
"""Stage 24 external-style load test (50–200 concurrent users, all roles).

Set LOAD_TEST_BASE_URL=http://localhost:8000 to hit a running API (Docker).
Without it, uses in-process TestClient (pilot; not true external load).
"""

from __future__ import annotations

import os
import random
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from uuid import uuid4

os.environ.setdefault("SKIP_STARTUP_VALIDATION", "true")
os.environ.setdefault("LOG_LEVEL", "ERROR")

_ROLES = ("admin", "supervisor", "worker", "investor")
_READ_PATHS = (
    "/runtime/projects?limit=50&offset=0",
    "/health/live",
)


def _login_testclient(client, username: str) -> str:
    response = client.post(
        "/auth/token",
        data={"username": username, "password": username},
    )
    response.raise_for_status()
    return response.json()["access_token"]


def _login_httpx(base_url: str, username: str) -> str:
    import httpx

    response = httpx.post(
        f"{base_url.rstrip('/')}/auth/token",
        data={"username": username, "password": username},
        timeout=30.0,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def _worker_inprocess(worker_id: int, iterations: int) -> tuple[list[float], int]:
    from fastapi.testclient import TestClient

    from backend.phase1.app import create_app

    client = TestClient(create_app())
    role = _ROLES[worker_id % len(_ROLES)]
    token = _login_testclient(client, role)
    headers = {"Authorization": f"Bearer {token}"}
    latencies: list[float] = []
    errors = 0

    project_id: str | None = None
    if role in ("admin", "supervisor") and worker_id % 5 == 0:
        code = f"LT-{worker_id}-{uuid4().hex[:6]}"
        created = client.post(
            "/planning/projects",
            json={"code": code, "name": f"Load {worker_id}", "status": "ACTIVE"},
            headers=headers,
        )
        if created.status_code == 201:
            project_id = created.json()["id"]

    for i in range(iterations):
        paths = list(_READ_PATHS)
        if project_id:
            paths.append(f"/runtime/projects/{project_id}/dashboard-summary")
            paths.append(
                f"/runtime/projects/{project_id}/workflow-steps-batch?limit=200",
            )
        path = paths[i % len(paths)]
        start = time.perf_counter()
        response = client.get(path, headers=headers)
        latencies.append((time.perf_counter() - start) * 1000)
        if response.status_code not in (200, 403, 404):
            errors += 1

        if project_id and role in ("admin", "supervisor", "worker") and i % 3 == 0:
            wo = client.post(
                "/planning/work-orders",
                json={
                    "project_id": project_id,
                    "work_order_number": f"WO-{worker_id}-{i}",
                    "title": "Load WO",
                    "planned_date": str(date.today()),
                },
                headers=headers,
            )
            if wo.status_code == 201:
                body = wo.json()
                report = client.post(
                    "/runtime/daily-reports",
                    json={
                        "work_order_id": body["id"],
                        "report_date": str(date.today()),
                        "status": "SUBMITTED",
                        "expected_work_order_updated_at": body["updated_at"],
                    },
                    headers=headers,
                )
                if report.status_code not in (201, 409, 422):
                    errors += 1

    return latencies, errors


def _worker_http(base_url: str, worker_id: int, iterations: int) -> tuple[list[float], int]:
    import httpx

    role = _ROLES[worker_id % len(_ROLES)]
    token = _login_httpx(base_url, role)
    headers = {"Authorization": f"Bearer {token}"}
    latencies: list[float] = []
    errors = 0

    with httpx.Client(base_url=base_url.rstrip("/"), timeout=30.0) as client:
        project_id: str | None = None
        if role in ("admin", "supervisor"):
            code = f"LT-{worker_id}-{uuid4().hex[:6]}"
            created = client.post(
                "/planning/projects",
                json={"code": code, "name": f"Load {worker_id}", "status": "ACTIVE"},
                headers=headers,
            )
            if created.status_code == 201:
                project_id = created.json()["id"]

        for i in range(iterations):
            if project_id and i % 2 == 0:
                path = f"/runtime/projects/{project_id}/workflow-steps-batch?limit=100"
            else:
                path = random.choice(_READ_PATHS)
            start = time.perf_counter()
            response = client.get(path, headers=headers)
            latencies.append((time.perf_counter() - start) * 1000)
            if response.status_code not in (200, 403, 404):
                errors += 1

    return latencies, errors


def main() -> int:
    virtual_users = int(os.getenv("LOAD_TEST_USERS", "50"))
    iterations = int(os.getenv("LOAD_TEST_ITERATIONS", "5"))
    base_url = os.getenv("LOAD_TEST_BASE_URL", "").strip()

    mode = "external" if base_url else "in-process"
    print(
        f"Stage 24 load test ({mode}): {virtual_users} users × "
        f"{iterations} iterations",
    )

    worker_fn = (
        (lambda wid, it: _worker_http(base_url, wid, it))
        if base_url
        else _worker_inprocess
    )

    all_latencies: list[float] = []
    total_errors = 0
    failures = 0
    start_all = time.perf_counter()

    max_workers = min(virtual_users, int(os.getenv("LOAD_TEST_MAX_WORKERS", "32")))
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [
            pool.submit(worker_fn, worker_id, iterations)
            for worker_id in range(virtual_users)
        ]
        for future in as_completed(futures):
            try:
                latencies, errors = future.result()
                all_latencies.extend(latencies)
                total_errors += errors
            except Exception as exc:  # noqa: BLE001
                failures += 1
                print(f"  worker failure: {exc}")

    wall_s = time.perf_counter() - start_all
    if not all_latencies:
        print("Load test failed — no successful samples.")
        return 1

    p50 = statistics.median(all_latencies)
    p95 = (
        statistics.quantiles(all_latencies, n=20)[18]
        if len(all_latencies) >= 20
        else max(all_latencies)
    )

    print(f"  wall time: {wall_s:.1f}s")
    print(f"  samples: {len(all_latencies)}")
    print(f"  worker failures: {failures}")
    print(f"  HTTP/logic errors: {total_errors}")
    print(f"  latency p50: {p50:.1f}ms")
    print(f"  latency p95: {p95:.1f}ms")
    print(f"  max: {max(all_latencies):.1f}ms")

    exit_code = 0
    if failures > 0:
        exit_code = 1
    if p95 > 5_000 and mode == "in-process":
        print("  note: in-process TestClient per thread inflates p95; use LOAD_TEST_BASE_URL")
    if total_errors > virtual_users:
        print("  elevated error count — review DB pool and concurrency guards")
        exit_code = 1

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
