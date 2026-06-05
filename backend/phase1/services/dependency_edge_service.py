"""Dependency edge service — authoritative edge substrate (P1).

Creates and deactivates explicit dependency edges with integrity validation and
lineage recording. Does not execute propagation, scheduling, or graph traversal.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from backend.phase1.dependency_edges.taxonomy import (
    EDGE_STATUS_ACTIVE,
    EDGE_STATUS_DEACTIVATED,
    ENTITY_WORKFLOW_STEP,
    semantics_for,
)
from backend.phase1.events.event_recording_service import EventRecordingService
from backend.phase1.integrity.dependency_edge_policy import (
    DependencyEdgeIntegrityError,
    validate_edge_active,
    validate_entity_pair_for_dependency_type,
    validate_no_direct_reverse_active_edge,
    validate_no_duplicate_active_edge,
    validate_no_self_link,
    validate_same_project,
)
from backend.phase1.models.operational_dependency_edge import OperationalDependencyEdge
from backend.phase1.repositories.activity_instance_repository import (
    ActivityInstanceRepository,
)
from backend.phase1.repositories.operational_dependency_edge_repository import (
    OperationalDependencyEdgeRepository,
)
from backend.phase1.repositories.operational_event_repository import (
    OperationalEventRepository,
)
from backend.phase1.repositories.work_order_repository import WorkOrderRepository
from backend.phase1.repositories.workflow_step_repository import WorkflowStepRepository


class DependencyEdgeService:
    """Owns explicit operational dependency edge mutations (P1 substrate)."""

    def __init__(
        self,
        edge_repository: OperationalDependencyEdgeRepository,
        workflow_step_repository: WorkflowStepRepository,
        activity_instance_repository: ActivityInstanceRepository,
        work_order_repository: WorkOrderRepository,
        event_recorder: EventRecordingService | None = None,
        event_repository: OperationalEventRepository | None = None,
        readiness_service: object | None = None,
    ) -> None:
        self._edges = edge_repository
        self._steps = workflow_step_repository
        self._activities = activity_instance_repository
        self._work_orders = work_order_repository
        self._event_recorder = event_recorder
        self._event_repository = event_repository
        self._readiness_service = readiness_service

    def create_edge(
        self,
        *,
        project_id: UUID,
        source_entity_type: str,
        source_entity_id: UUID,
        target_entity_type: str,
        target_entity_id: UUID,
        dependency_type: str,
        actor: str,
        metadata: dict[str, Any] | None = None,
    ) -> OperationalDependencyEdge:
        validate_no_self_link(
            source_entity_type=source_entity_type,
            source_entity_id=source_entity_id,
            target_entity_type=target_entity_type,
            target_entity_id=target_entity_id,
        )
        validate_entity_pair_for_dependency_type(
            dependency_type=dependency_type,
            source_entity_type=source_entity_type,
            target_entity_type=target_entity_type,
        )

        source_project = self._resolve_project_id(source_entity_type, source_entity_id)
        target_project = self._resolve_project_id(target_entity_type, target_entity_id)
        validate_same_project(
            project_id=project_id,
            source_project_id=source_project,
            target_project_id=target_project,
        )

        existing = self._edges.find_active_identity(
            project_id=project_id,
            source_entity_type=source_entity_type,
            source_entity_id=source_entity_id,
            target_entity_type=target_entity_type,
            target_entity_id=target_entity_id,
            dependency_type=dependency_type,
        )
        validate_no_duplicate_active_edge(existing)

        reverse = self._edges.find_active_reverse(
            project_id=project_id,
            source_entity_type=source_entity_type,
            source_entity_id=source_entity_id,
            target_entity_type=target_entity_type,
            target_entity_id=target_entity_id,
            dependency_type=dependency_type,
        )
        validate_no_direct_reverse_active_edge(
            dependency_type=dependency_type,
            reverse_exists=reverse is not None,
        )

        stamped = semantics_for(dependency_type)
        edge = OperationalDependencyEdge(
            project_id=project_id,
            source_entity_type=source_entity_type,
            source_entity_id=source_entity_id,
            target_entity_type=target_entity_type,
            target_entity_id=target_entity_id,
            dependency_type=dependency_type,
            authority_level=stamped.authority_level,
            blocking_semantics=stamped.blocking_semantics,
            propagation_semantics=stamped.propagation_semantics,
            lifecycle_status=EDGE_STATUS_ACTIVE,
            created_by=actor,
            edge_metadata=metadata,
        )
        created = self._edges.create(edge)

        event = None
        if self._event_recorder is not None:
            event = self._event_recorder.record_dependency_edge_created(
                edge_id=created.id,
                project_id=project_id,
                source_entity_type=source_entity_type,
                source_entity_id=source_entity_id,
                target_entity_type=target_entity_type,
                target_entity_id=target_entity_id,
                dependency_type=dependency_type,
                authority_level=stamped.authority_level,
                blocking_semantics=stamped.blocking_semantics,
                propagation_semantics=stamped.propagation_semantics,
                actor=actor,
                metadata=metadata,
            )
        self._refresh_target_readiness(
            target_entity_type=target_entity_type,
            target_entity_id=target_entity_id,
            actor=actor,
            trigger="dependency_edge_created",
            causality_reference=event.event_id if event is not None else None,
        )
        return created

    def deactivate_edge(
        self,
        *,
        project_id: UUID,
        edge_id: UUID,
        actor: str,
        reason: str | None = None,
    ) -> OperationalDependencyEdge:
        edge = self._edges.get_by_id(edge_id)
        if edge is None or edge.project_id != project_id:
            msg = f"dependency edge {edge_id} not found for project"
            raise DependencyEdgeIntegrityError(msg)
        validate_edge_active(edge)

        edge.lifecycle_status = EDGE_STATUS_DEACTIVATED
        edge.deactivated_at = datetime.now(timezone.utc)
        edge.deactivated_by = actor
        edge.deactivation_reason = reason
        updated = self._edges.update(edge)

        event = None
        if self._event_recorder is not None:
            event = self._event_recorder.record_dependency_edge_deactivated(
                edge_id=updated.id,
                project_id=project_id,
                dependency_type=updated.dependency_type,
                actor=actor,
                reason=reason,
            )
        self._refresh_target_readiness(
            target_entity_type=edge.target_entity_type,
            target_entity_id=edge.target_entity_id,
            actor=actor,
            trigger="dependency_edge_deactivated",
            causality_reference=event.event_id if event is not None else None,
        )
        return updated

    def get_edge(self, project_id: UUID, edge_id: UUID) -> OperationalDependencyEdge | None:
        edge = self._edges.get_by_id(edge_id)
        if edge is None or edge.project_id != project_id:
            return None
        return edge

    def list_edges(
        self,
        project_id: UUID,
        *,
        dependency_type: str | None = None,
        lifecycle_status: str | None = EDGE_STATUS_ACTIVE,
        offset: int = 0,
        limit: int = 200,
    ) -> list[OperationalDependencyEdge]:
        return self._edges.list_for_project(
            project_id,
            dependency_type=dependency_type,
            lifecycle_status=lifecycle_status,
            offset=offset,
            limit=limit,
        )

    def trace_entity(
        self,
        project_id: UUID,
        *,
        entity_type: str,
        entity_id: UUID,
        lifecycle_status: str | None = EDGE_STATUS_ACTIVE,
    ) -> dict[str, list[OperationalDependencyEdge]]:
        entity_project = self._resolve_project_id(entity_type, entity_id)
        if entity_project != project_id:
            raise DependencyEdgeIntegrityError(
                "entity does not belong to the requested project",
            )
        outgoing, incoming = self._edges.trace_entity(
            project_id,
            entity_type=entity_type,
            entity_id=entity_id,
            lifecycle_status=lifecycle_status,
        )
        return {"outgoing": outgoing, "incoming": incoming}

    def list_lineage(self, edge_id: UUID) -> list:
        if self._event_repository is None:
            return []
        from backend.phase1.events.taxonomy import AGGREGATE_DEPENDENCY_EDGE

        return self._event_repository.list_for_aggregate(
            AGGREGATE_DEPENDENCY_EDGE,
            edge_id,
        )

    def _refresh_target_readiness(
        self,
        *,
        target_entity_type: str,
        target_entity_id: UUID,
        actor: str | None,
        trigger: str,
        causality_reference: UUID | None,
    ) -> None:
        if self._readiness_service is None:
            return
        if target_entity_type != ENTITY_WORKFLOW_STEP:
            return
        refresh = getattr(self._readiness_service, "refresh_for_workflow_step", None)
        if refresh is None:
            return
        refresh(
            target_entity_id,
            actor=actor,
            trigger=trigger,
            causality_reference=causality_reference,
        )

    def _resolve_project_id(self, entity_type: str, entity_id: UUID) -> UUID:
        if entity_type == "workflow_step":
            step = self._steps.get_by_id(entity_id)
            if step is None:
                raise DependencyEdgeIntegrityError(
                    f"workflow_step {entity_id} not found",
                )
            activity = self._activities.get_by_id(step.activity_instance_id)
            if activity is None:
                raise DependencyEdgeIntegrityError(
                    f"activity_instance for workflow_step {entity_id} not found",
                )
            return activity.project_id

        if entity_type == "activity_instance":
            activity = self._activities.get_by_id(entity_id)
            if activity is None:
                raise DependencyEdgeIntegrityError(
                    f"activity_instance {entity_id} not found",
                )
            return activity.project_id

        if entity_type == "work_order":
            work_order = self._work_orders.get_by_id(entity_id)
            if work_order is None:
                raise DependencyEdgeIntegrityError(
                    f"work_order {entity_id} not found",
                )
            return work_order.project_id

        raise DependencyEdgeIntegrityError(f"unsupported entity type {entity_type!r}")
