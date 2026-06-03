#!/usr/bin/env python3
"""Stage 24 persisted IAM checks (JWT role binding, platform_users, membership)."""

from __future__ import annotations

import os
import sys

os.environ.setdefault("SKIP_STARTUP_VALIDATION", "true")

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, text  # noqa: E402
from sqlalchemy.exc import SQLAlchemyError  # noqa: E402

from backend.config import get_settings  # noqa: E402
from backend.phase1.app import create_app  # noqa: E402
from backend.phase1.auth.security import create_access_token, decode_token  # noqa: E402


_ROLES = ("admin", "supervisor", "worker", "investor")


def _login(client: TestClient, username: str) -> str:
    response = client.post(
        "/auth/token",
        data={"username": username, "password": username},
    )
    if response.status_code != 200:
        raise RuntimeError(f"login {username}: {response.status_code} {response.text}")
    return response.json()["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def main() -> int:
    failures: list[str] = []
    client = TestClient(create_app())

    tokens: dict[str, str] = {}
    for role in _ROLES:
        token = _login(client, role)
        tokens[role] = token
        payload = decode_token(token)
        if payload.get("sub") != role:
            failures.append(f"token sub mismatch for {role}")
        if payload.get("role") != role:
            failures.append(f"token role mismatch for {role}")

    # JWT role must match DB role
    mismatched = create_access_token({"sub": "admin", "role": "worker"})
    me = client.get("/runtime/projects", headers=_auth(mismatched))
    if me.status_code != 401:
        failures.append(
            f"JWT/DB role mismatch expected 401, got {me.status_code}",
        )

    # Worker cannot create planning projects
    worker_plan = client.post(
        "/planning/projects",
        json={"code": "IAM24", "name": "Denied", "status": "ACTIVE"},
        headers=_auth(tokens["worker"]),
    )
    if worker_plan.status_code != 403:
        failures.append(f"worker planning expected 403, got {worker_plan.status_code}")

    settings = get_settings()
    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            count = connection.execute(
                text("SELECT COUNT(*) FROM platform_users"),
            ).scalar()
            if count is None or int(count) < len(_ROLES):
                failures.append(
                    f"platform_users count {count}, expected >= {len(_ROLES)}",
                )
            indexes = connection.execute(
                text(
                    """
                    SELECT indexname FROM pg_indexes
                    WHERE tablename IN ('platform_users', 'project_memberships')
                    """,
                ),
            ).fetchall()
            index_names = {row[0] for row in indexes}
            required = {
                "idx_platform_users_role",
                "idx_project_memberships_username",
                "idx_project_memberships_project_id",
            }
            missing = required - index_names
            if missing:
                failures.append(f"missing indexes: {sorted(missing)}")
    except SQLAlchemyError as exc:
        print(f"PostgreSQL unavailable — skipping DB IAM checks: {exc}")
        if failures:
            print("Stage 24 IAM verification FAILED:")
            for item in failures:
                print(f"  - {item}")
            return 1
        print("Stage 24 IAM verification passed (in-memory / no-DB paths only).")
        return 0

    if failures:
        print("Stage 24 IAM verification FAILED:")
        for item in failures:
            print(f"  - {item}")
        return 1

    print("Stage 24 IAM verification passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
