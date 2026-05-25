from backend.lifecycle.models.entities import (
    OperationalBlocker,
    ExecutionDependency,
)
from backend.lifecycle.utils.enums import (
    BlockerResolutionState,
    ReadinessStatus,
)


def evaluate_dependencies(
    dependencies: list[ExecutionDependency],
    blockers: list[OperationalBlocker],
) -> dict:
    open_blockers = [
        blocker
        for blocker in blockers
        if blocker.resolution_state
        in {
            BlockerResolutionState.OPEN.value,
            BlockerResolutionState.IN_PROGRESS.value,
            BlockerResolutionState.ESCALATED.value,
        }
    ]

    unsatisfied = [
        dep for dep in dependencies if not dep.is_satisfied
    ]

    factors = []

    for dep in unsatisfied:
        factors.append({
            "factor": "dependency",
            "passed": False,
            "message": dep.description or dep.dependency_type,
        })

    for blocker in open_blockers:
        factors.append({
            "factor": blocker.blocker_type,
            "passed": False,
            "message": blocker.title,
            "severity": blocker.severity,
        })

    if not factors:
        return {
            "blocked": False,
            "open_blocker_count": 0,
            "unsatisfied_dependency_count": 0,
            "factors": [],
        }

    return {
        "blocked": True,
        "open_blocker_count": len(open_blockers),
        "unsatisfied_dependency_count": len(unsatisfied),
        "factors": factors,
    }


def map_dependency_to_readiness(
    dependency_result: dict,
    approval_pending: bool,
    workforce_ready: bool = True,
) -> dict:
    factors = list(dependency_result.get("factors", []))

    if approval_pending:
        factors.append({
            "factor": "approval",
            "passed": False,
            "message": "Pending operational approval",
        })

    if not workforce_ready:
        factors.append({
            "factor": "workforce",
            "passed": False,
            "message": "Workforce not ready",
        })

    failed = [f for f in factors if not f.get("passed", True)]

    if not failed:
        return {
            "status": ReadinessStatus.READY.value,
            "score": 100.0,
            "factors": factors,
            "can_start": True,
        }

    if len(failed) <= 2:
        score = max(100 - (len(failed) * 20), 0)
        return {
            "status": ReadinessStatus.PARTIALLY_READY.value,
            "score": score,
            "factors": factors,
            "can_start": False,
        }

    return {
        "status": ReadinessStatus.BLOCKED.value,
        "score": max(100 - (len(failed) * 25), 0),
        "factors": factors,
        "can_start": False,
    }
