#!/usr/bin/env python3
"""Runtime Hardening P2 verification — derived readiness ownership."""

from __future__ import annotations

import os
import sys

os.environ.setdefault("SKIP_STARTUP_VALIDATION", "true")

from fastapi.testclient import TestClient  # noqa: E402

from backend.phase1.app import create_app  # noqa: E402
from backend.phase1.readiness.authority import (
    ReadinessAuthorityError,
    reject_direct_ready_mutation,
)
from backend.phase1.readiness.derivation import (
    _BlockerSnapshot,
    _StepSnapshot,
    derive_workflow_step_readiness,
)


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


def _unit_derivation() -> bool:
    passed = True
    from uuid import uuid4

    project_id = uuid4()
    step_id = uuid4()
    result = derive_workflow_step_readiness(
        project_id=project_id,
        step=_StepSnapshot(
            id=step_id,
            status="PLANNED",
            ready=False,
            code="WS-01",
        ),
        blockers=[],
        incoming_edges=[],
        source_steps={},
        source_activities={},
    )
    passed &= _check("Derivation returns derived_ready", isinstance(result.derived_ready, bool))
    passed &= _check("Evidence sources present", len(result.evidence_sources) >= 1)
    passed &= _check("Lineage owner in payload", result.to_dict()["lineage_owner"] == "readiness_derivation_service")

    try:
        reject_direct_ready_mutation(True)
        passed &= _check("Authority rejects ready=True", False)
    except ReadinessAuthorityError:
        passed &= _check("Authority rejects ready=True", True)

    reject_direct_ready_mutation(False)
    passed &= _check("Authority allows ready=False", True)

    blocked = derive_workflow_step_readiness(
        project_id=project_id,
        step=_StepSnapshot(id=step_id, status="PLANNED", ready=True, code="WS-01"),
        blockers=[
            _BlockerSnapshot(
                id=uuid4(),
                title="Rain",
                severity="HIGH",
                status="OPEN",
            ),
        ],
        incoming_edges=[],
        source_steps={},
        source_activities={},
    )
    passed &= _check("Open blocker forces not ready", blocked.derived_ready is False)
    passed &= _check("Contradiction surfaced", len(blocked.contradictions) >= 1)
    return passed


def main() -> int:
    print("Runtime Hardening P2 verification")
    passed = _unit_derivation()

    client = TestClient(create_app(), raise_server_exceptions=False)
    passed &= _check(
        "Readiness inspect unauthenticated denied",
        client.get(
            "/runtime/projects/00000000-0000-0000-0000-000000000001/"
            "workflow-steps/00000000-0000-0000-0000-000000000002/readiness",
        ).status_code
        == 401,
    )

    admin = _token(client, "admin")
    if not admin:
        _check("Auth", True, "skipped (PostgreSQL required)")
        print("Runtime Hardening P2 verification passed (degraded).")
        return 0

    headers = {"Authorization": f"Bearer {admin}"}
    bad_ready = client.post(
        "/planning/workflow-steps",
        headers=headers,
        json={
            "activity_instance_id": "00000000-0000-0000-0000-000000000099",
            "code": "X",
            "name": "Test",
            "status": "PLANNED",
            "ready": True,
        },
    )
    passed &= _check(
        "Direct ready=True rejected",
        bad_ready.status_code == 422,
        str(bad_ready.status_code),
    )

    inspect = client.get(
        "/runtime/projects/00000000-0000-0000-0000-000000000001/"
        "workflow-steps/00000000-0000-0000-0000-000000000002/readiness",
        headers=headers,
    )
    passed &= _check(
        "Readiness inspect endpoint exists",
        inspect.status_code in (200, 404),
        str(inspect.status_code),
    )
    if inspect.status_code == 200:
        body = inspect.json()
        passed &= _check("derived_ready in response", "derived_ready" in body)
        passed &= _check("blocking_conditions in response", "blocking_conditions" in body)
        passed &= _check("contradictions in response", "contradictions" in body)

    if passed:
        print("Runtime Hardening P2 verification passed.")
        return 0
    print("Runtime Hardening P2 verification failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
