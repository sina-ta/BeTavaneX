"""Derived readiness inspection (Runtime Hardening P2) — read-only visibility."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.phase1.auth.auth import User
from backend.phase1.auth.operational_audit import log_operational_action
from backend.phase1.auth.project_access import ProjectAccessService
from backend.phase1.auth.role_policy import require_runtime_reader
from backend.phase1.dependencies.auth import get_project_access_service
from backend.phase1.dependencies.services import get_readiness_derivation_service
from backend.phase1.readiness.derivation import ReadinessDerivationResult
from backend.phase1.schemas.readiness_schema import (
    ReadinessInterpretationRead,
    ReadinessLineageRead,
)
from backend.phase1.services.readiness_derivation_service import (
    ReadinessDerivationService,
)

router = APIRouter(prefix="/runtime/projects", tags=["runtime-readiness"])


def _to_read_model(result: ReadinessDerivationResult) -> ReadinessInterpretationRead:
    payload = result.to_dict()
    return ReadinessInterpretationRead.model_validate(payload)


@router.get(
    "/{project_id}/workflow-steps/{workflow_step_id}/readiness",
    response_model=ReadinessInterpretationRead,
)
def inspect_workflow_step_readiness(
    project_id: UUID,
    workflow_step_id: UUID,
    current_user: User = Depends(require_runtime_reader),
    access: ProjectAccessService = Depends(get_project_access_service),
    service: ReadinessDerivationService = Depends(get_readiness_derivation_service),
) -> ReadinessInterpretationRead:
    access.ensure_project_access(current_user, project_id)
    try:
        result = service.inspect_workflow_step(workflow_step_id, project_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    log_operational_action(
        current_user,
        "readiness_inspection_read",
        mutation_category="query",
        project_id=project_id,
        resource_type="workflow_step",
        resource_id=workflow_step_id,
        detail={
            "derived_ready": result.derived_ready,
            "contradiction_count": len(result.contradictions),
        },
    )
    return _to_read_model(result)


@router.get(
    "/{project_id}/workflow-steps/{workflow_step_id}/readiness/lineage",
    response_model=list[ReadinessLineageRead],
)
def list_workflow_step_readiness_lineage(
    project_id: UUID,
    workflow_step_id: UUID,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    current_user: User = Depends(require_runtime_reader),
    access: ProjectAccessService = Depends(get_project_access_service),
    service: ReadinessDerivationService = Depends(get_readiness_derivation_service),
) -> list[ReadinessLineageRead]:
    access.ensure_project_access(current_user, project_id)
    events = service.list_lineage(
        workflow_step_id,
        offset=offset,
        limit=limit,
    )
    return [
        ReadinessLineageRead(
            event_id=str(event.event_id),
            event_type=event.event_type,
            occurred_at=event.occurred_at.isoformat(),
            actor=event.actor,
            payload=event.payload or {},
        )
        for event in events
    ]
