"""Dependency edge router — explicit substrate visibility (P1).

Read-only inspection/trace/lineage plus minimal create/deactivate mutations.
No propagation, scheduling, or orchestration.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.phase1.auth.auth import User
from backend.phase1.auth.dependencies import get_current_active_user
from backend.phase1.auth.operational_audit import log_operational_action
from backend.phase1.auth.project_access import ProjectAccessService
from backend.phase1.auth.role_policy import require_planning_actor, require_runtime_reader
from backend.phase1.dependencies.auth import get_project_access_service
from backend.phase1.dependencies.services import get_dependency_edge_service
from backend.phase1.integrity.dependency_edge_policy import DependencyEdgeIntegrityError
from backend.phase1.schemas.dependency_edge_schema import (
    DependencyEdgeCreate,
    DependencyEdgeDeactivate,
    DependencyEdgeLineageRead,
    DependencyEdgeRead,
    DependencyEdgeTraceRead,
    OperationalEventRead,
)
from backend.phase1.services.dependency_edge_service import DependencyEdgeService

router = APIRouter(prefix="/runtime/projects", tags=["runtime-dependencies"])


def _ensure_project_access(
    project_id: UUID,
    user: User,
    access: ProjectAccessService,
) -> None:
    access.ensure_project_access(user, project_id)


@router.get(
    "/{project_id}/dependency-edges",
    response_model=list[DependencyEdgeRead],
)
def list_dependency_edges(
    project_id: UUID,
    dependency_type: str | None = Query(default=None),
    lifecycle_status: str | None = Query(default="active"),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=200, ge=1, le=500),
    current_user: User = Depends(require_runtime_reader),
    access: ProjectAccessService = Depends(get_project_access_service),
    service: DependencyEdgeService = Depends(get_dependency_edge_service),
) -> list[DependencyEdgeRead]:
    _ensure_project_access(project_id, current_user, access)
    edges = service.list_edges(
        project_id,
        dependency_type=dependency_type,
        lifecycle_status=lifecycle_status,
        offset=offset,
        limit=limit,
    )
    return [DependencyEdgeRead.model_validate(edge) for edge in edges]


@router.get(
    "/{project_id}/dependency-edges/trace",
    response_model=DependencyEdgeTraceRead,
)
def trace_dependency_edges(
    project_id: UUID,
    entity_type: str = Query(...),
    entity_id: UUID = Query(...),
    lifecycle_status: str | None = Query(default="active"),
    current_user: User = Depends(require_runtime_reader),
    access: ProjectAccessService = Depends(get_project_access_service),
    service: DependencyEdgeService = Depends(get_dependency_edge_service),
) -> DependencyEdgeTraceRead:
    _ensure_project_access(project_id, current_user, access)
    try:
        traced = service.trace_entity(
            project_id,
            entity_type=entity_type,
            entity_id=entity_id,
            lifecycle_status=lifecycle_status,
        )
    except DependencyEdgeIntegrityError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return DependencyEdgeTraceRead(
        entity_type=entity_type,
        entity_id=entity_id,
        outgoing=[DependencyEdgeRead.model_validate(e) for e in traced["outgoing"]],
        incoming=[DependencyEdgeRead.model_validate(e) for e in traced["incoming"]],
    )


@router.get(
    "/{project_id}/dependency-edges/{edge_id}",
    response_model=DependencyEdgeRead,
)
def get_dependency_edge(
    project_id: UUID,
    edge_id: UUID,
    current_user: User = Depends(require_runtime_reader),
    access: ProjectAccessService = Depends(get_project_access_service),
    service: DependencyEdgeService = Depends(get_dependency_edge_service),
) -> DependencyEdgeRead:
    _ensure_project_access(project_id, current_user, access)
    edge = service.get_edge(project_id, edge_id)
    if edge is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Edge not found")
    return DependencyEdgeRead.model_validate(edge)


@router.get(
    "/{project_id}/dependency-edges/{edge_id}/lineage",
    response_model=DependencyEdgeLineageRead,
)
def get_dependency_edge_lineage(
    project_id: UUID,
    edge_id: UUID,
    current_user: User = Depends(require_runtime_reader),
    access: ProjectAccessService = Depends(get_project_access_service),
    service: DependencyEdgeService = Depends(get_dependency_edge_service),
) -> DependencyEdgeLineageRead:
    _ensure_project_access(project_id, current_user, access)
    edge = service.get_edge(project_id, edge_id)
    if edge is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Edge not found")
    events = service.list_lineage(edge_id)
    return DependencyEdgeLineageRead(
        edge_id=edge_id,
        events=[OperationalEventRead.model_validate(event) for event in events],
    )


@router.post(
    "/{project_id}/dependency-edges",
    response_model=DependencyEdgeRead,
    status_code=status.HTTP_201_CREATED,
)
def create_dependency_edge(
    project_id: UUID,
    payload: DependencyEdgeCreate,
    current_user: User = Depends(require_planning_actor),
    access: ProjectAccessService = Depends(get_project_access_service),
    service: DependencyEdgeService = Depends(get_dependency_edge_service),
) -> DependencyEdgeRead:
    _ensure_project_access(project_id, current_user, access)
    try:
        edge = service.create_edge(
            project_id=project_id,
            source_entity_type=payload.source_entity_type,
            source_entity_id=payload.source_entity_id,
            target_entity_type=payload.target_entity_type,
            target_entity_id=payload.target_entity_id,
            dependency_type=payload.dependency_type,
            actor=current_user.username,
            metadata=payload.metadata,
        )
    except DependencyEdgeIntegrityError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    log_operational_action(
        username=current_user.username,
        role=current_user.role,
        mutation_category="planning",
        action="create_dependency_edge",
        project_id=project_id,
        resource_type="dependency_edge",
        resource_id=edge.id,
        detail={
            "dependency_type": edge.dependency_type,
            "source_entity_type": edge.source_entity_type,
            "source_entity_id": str(edge.source_entity_id),
            "target_entity_type": edge.target_entity_type,
            "target_entity_id": str(edge.target_entity_id),
        },
    )
    return DependencyEdgeRead.model_validate(edge)


@router.post(
    "/{project_id}/dependency-edges/{edge_id}/deactivate",
    response_model=DependencyEdgeRead,
)
def deactivate_dependency_edge(
    project_id: UUID,
    edge_id: UUID,
    payload: DependencyEdgeDeactivate,
    current_user: User = Depends(require_planning_actor),
    access: ProjectAccessService = Depends(get_project_access_service),
    service: DependencyEdgeService = Depends(get_dependency_edge_service),
) -> DependencyEdgeRead:
    _ensure_project_access(project_id, current_user, access)
    try:
        edge = service.deactivate_edge(
            project_id=project_id,
            edge_id=edge_id,
            actor=current_user.username,
            reason=payload.reason,
        )
    except DependencyEdgeIntegrityError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    log_operational_action(
        username=current_user.username,
        role=current_user.role,
        mutation_category="planning",
        action="deactivate_dependency_edge",
        project_id=project_id,
        resource_type="dependency_edge",
        resource_id=edge.id,
        detail={"dependency_type": edge.dependency_type, "reason": payload.reason},
    )
    return DependencyEdgeRead.model_validate(edge)
