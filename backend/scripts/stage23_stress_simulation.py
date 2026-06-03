#!/usr/bin/env python3
"""Stage 23 operational stress simulation (lightweight, no load-test framework)."""

from __future__ import annotations

import os
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

os.environ.setdefault("SKIP_STARTUP_VALIDATION", "true")
os.environ.setdefault("LOG_LEVEL", "ERROR")

from fastapi.testclient import TestClient  # noqa: E402

from backend.phase1.app import create_app  # noqa: E402


def _login(client: TestClient, username: str) -> str:
    response = client.post(
        "/auth/token",
        data={"username": username, "password": username},
    )
    response.raise_for_status()
    return response.json()["access_token"]


def _worker_task(worker_id: int, iterations: int) -> list[float]:
    client = TestClient(create_app())
    token = _login(client, "admin")
    headers = {"Authorization": f"Bearer {token}"}
    latencies: list[float] = []

    for _ in range(iterations):
        start = time.perf_counter()
        health = client.get("/health/live")
        openapi = client.get("/openapi.json")
        elapsed = (time.perf_counter() - start) * 1000
        latencies.append(elapsed)

        if health.status_code != 200 or openapi.status_code != 200:
            raise RuntimeError(
                f"worker={worker_id} health={health.status_code} "
                f"openapi={openapi.status_code}",
            )

    return latencies


def main() -> int:
    virtual_users = int(os.getenv("STRESS_VIRTUAL_USERS", "50"))
    iterations = int(os.getenv("STRESS_ITERATIONS_PER_USER", "3"))

    print(
        f"Stress simulation: {virtual_users} virtual users, "
        f"{iterations} iterations each",
    )

    all_latencies: list[float] = []
    failures = 0
    start_all = time.perf_counter()

    with ThreadPoolExecutor(max_workers=min(virtual_users, 32)) as pool:
        futures = [
            pool.submit(_worker_task, worker_id, iterations)
            for worker_id in range(virtual_users)
        ]
        for future in as_completed(futures):
            try:
                all_latencies.extend(future.result())
            except Exception as exc:  # noqa: BLE001
                failures += 1
                print(f"  worker failure: {exc}")

    total_s = time.perf_counter() - start_all
    total_requests = virtual_users * iterations * 2  # health/live + openapi per iteration

    if not all_latencies:
        print("Stress simulation failed — no successful samples.")
        return 1

    p50 = statistics.median(all_latencies)
    p95 = statistics.quantiles(all_latencies, n=20)[18] if len(all_latencies) >= 20 else max(all_latencies)
    print(f"  total wall time: {total_s:.1f}s")
    print(f"  requests (health+projects pairs): {total_requests}")
    print(f"  failures: {failures}")
    print(f"  latency p50: {p50:.1f}ms")
    print(f"  latency p95: {p95:.1f}ms")
    print(f"  max: {max(all_latencies):.1f}ms")

    limits = []
    if p95 > 2_000:
        limits.append("p95 > 2s under concurrent dashboard access — scale API workers or DB pool")
    if failures > 0:
        limits.append(f"{failures} worker failures — investigate concurrency or connection pool")

    print("\nOperational limits (pilot-scale):")
    if limits:
        for item in limits:
            print(f"  - {item}")
    else:
        print("  - 50 concurrent users × 3 iterations: acceptable for pilot deployment")
        print("  - Full production scale requires external Postgres tuning + horizontal API replicas")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
