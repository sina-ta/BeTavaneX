"""Event recording service — the single sanctioned way to append lineage events.

Responsibilities:
  * build a valid ``OperationalEvent`` (typed, timestamped, actor-attributed)
  * validate the event type against the taxonomy
  * delegate the append to the append-only repository

It performs no business logic and reads no domain state. It is invoked at
existing operational chokepoints (see ``docs/cosc/event-ledger-foundation.md``).
Recording shares the request-scoped Session, so an event is committed in the same
transaction as the operation it records.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from backend.phase1.events.taxonomy import (
    EVENT_AGGREGATE_TYPE,
    EVENT_APPROVAL_COMPLETED,
    EVENT_BLOCKER_REGISTERED,
    EVENT_BLOCKER_RESOLVED,
    EVENT_DAILY_REPORT_SUBMITTED,
    EVENT_DEPENDENCY_EDGE_CREATED,
    EVENT_DEPENDENCY_EDGE_DEACTIVATED,
    EVENT_READINESS_BLOCKED,
    EVENT_READINESS_EVALUATED,
    EVENT_READINESS_RECOVERED,
    EVENT_WORK_ORDER_ASSIGNED,
    is_supported_event_type,
)
from backend.phase1.models.operational_event import OperationalEvent
from backend.phase1.repositories.operational_event_repository import (
    OperationalEventRepository,
)

_SYSTEM_ACTOR = "system"


class EventRecordingService:
    """Appends operational lineage events through the append-only repository."""

    def __init__(self, event_repository: OperationalEventRepository) -> None:
        self._events = event_repository

    def record(
        self,
        *,
        event_type: str,
        aggregate_id: UUID,
        actor: str | None,
        payload: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        causality_reference: UUID | None = None,
        aggregate_type: str | None = None,
    ) -> OperationalEvent:
        if not is_supported_event_type(event_type):
            msg = f"Unsupported operational event type: {event_type}"
            raise ValueError(msg)

        resolved_aggregate_type = aggregate_type or EVENT_AGGREGATE_TYPE[event_type]
        event = OperationalEvent(
            event_type=event_type,
            aggregate_type=resolved_aggregate_type,
            aggregate_id=aggregate_id,
            actor=actor or _SYSTEM_ACTOR,
            occurred_at=datetime.now(timezone.utc),
            causality_reference=causality_reference,
            payload=_jsonable(payload or {}),
            event_metadata=_jsonable(metadata or {}),
        )
        return self._events.append(event)

    # --- Typed convenience recorders for the five foundational events ---------

    def record_work_order_assigned(
        self,
        *,
        work_order_id: UUID,
        workflow_step_id: UUID,
        execution_weight: Decimal,
        actor: str | None,
        project_id: UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> OperationalEvent:
        return self.record(
            event_type=EVENT_WORK_ORDER_ASSIGNED,
            aggregate_id=work_order_id,
            actor=actor,
            payload={
                "work_order_id": str(work_order_id),
                "workflow_step_id": str(workflow_step_id),
                "execution_weight": str(execution_weight),
            },
            metadata=_with_project(metadata, project_id),
        )

    def record_daily_report_submitted(
        self,
        *,
        daily_report_id: UUID,
        work_order_id: UUID,
        actor: str | None,
        report_status: str | None = None,
        project_id: UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> OperationalEvent:
        return self.record(
            event_type=EVENT_DAILY_REPORT_SUBMITTED,
            aggregate_id=daily_report_id,
            actor=actor,
            payload={
                "daily_report_id": str(daily_report_id),
                "work_order_id": str(work_order_id),
                "status": report_status,
            },
            metadata=_with_project(metadata, project_id),
        )

    def record_approval_completed(
        self,
        *,
        workflow_step_id: UUID,
        approval_id: UUID,
        approval_type: str,
        actor: str | None,
        project_id: UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> OperationalEvent:
        return self.record(
            event_type=EVENT_APPROVAL_COMPLETED,
            aggregate_id=workflow_step_id,
            actor=actor,
            payload={
                "workflow_step_id": str(workflow_step_id),
                "approval_id": str(approval_id),
                "approval_type": approval_type,
            },
            metadata=_with_project(metadata, project_id),
        )

    def record_blocker_registered(
        self,
        *,
        blocker_id: UUID,
        workflow_step_id: UUID,
        blocker_type: str,
        severity: str,
        actor: str | None,
        metadata: dict[str, Any] | None = None,
    ) -> OperationalEvent:
        return self.record(
            event_type=EVENT_BLOCKER_REGISTERED,
            aggregate_id=blocker_id,
            actor=actor,
            payload={
                "blocker_id": str(blocker_id),
                "workflow_step_id": str(workflow_step_id),
                "blocker_type": blocker_type,
                "severity": severity,
            },
            metadata=metadata,
        )

    def record_dependency_edge_created(
        self,
        *,
        edge_id: UUID,
        project_id: UUID,
        source_entity_type: str,
        source_entity_id: UUID,
        target_entity_type: str,
        target_entity_id: UUID,
        dependency_type: str,
        authority_level: str,
        blocking_semantics: str,
        propagation_semantics: str,
        actor: str | None,
        metadata: dict[str, Any] | None = None,
    ) -> OperationalEvent:
        return self.record(
            event_type=EVENT_DEPENDENCY_EDGE_CREATED,
            aggregate_id=edge_id,
            actor=actor,
            payload={
                "edge_id": str(edge_id),
                "project_id": str(project_id),
                "source_entity_type": source_entity_type,
                "source_entity_id": str(source_entity_id),
                "target_entity_type": target_entity_type,
                "target_entity_id": str(target_entity_id),
                "dependency_type": dependency_type,
                "authority_level": authority_level,
                "blocking_semantics": blocking_semantics,
                "propagation_semantics": propagation_semantics,
            },
            metadata=_with_project(metadata, project_id),
        )

    def record_dependency_edge_deactivated(
        self,
        *,
        edge_id: UUID,
        project_id: UUID,
        dependency_type: str,
        actor: str | None,
        reason: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> OperationalEvent:
        return self.record(
            event_type=EVENT_DEPENDENCY_EDGE_DEACTIVATED,
            aggregate_id=edge_id,
            actor=actor,
            payload={
                "edge_id": str(edge_id),
                "project_id": str(project_id),
                "dependency_type": dependency_type,
                "reason": reason,
            },
            metadata=_with_project(metadata, project_id),
        )

    def record_readiness_evaluated(
        self,
        *,
        workflow_step_id: UUID,
        actor: str | None,
        payload: dict[str, Any],
        project_id: UUID | None = None,
        causality_reference: UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> OperationalEvent:
        return self.record(
            event_type=EVENT_READINESS_EVALUATED,
            aggregate_id=workflow_step_id,
            actor=actor,
            causality_reference=causality_reference,
            payload=payload,
            metadata=_with_project(metadata, project_id),
        )

    def record_readiness_blocked(
        self,
        *,
        workflow_step_id: UUID,
        actor: str | None,
        payload: dict[str, Any],
        project_id: UUID | None = None,
        causality_reference: UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> OperationalEvent:
        return self.record(
            event_type=EVENT_READINESS_BLOCKED,
            aggregate_id=workflow_step_id,
            actor=actor,
            causality_reference=causality_reference,
            payload=payload,
            metadata=_with_project(metadata, project_id),
        )

    def record_readiness_recovered(
        self,
        *,
        workflow_step_id: UUID,
        actor: str | None,
        payload: dict[str, Any],
        project_id: UUID | None = None,
        causality_reference: UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> OperationalEvent:
        return self.record(
            event_type=EVENT_READINESS_RECOVERED,
            aggregate_id=workflow_step_id,
            actor=actor,
            causality_reference=causality_reference,
            payload=payload,
            metadata=_with_project(metadata, project_id),
        )

    def record_blocker_resolved(
        self,
        *,
        blocker_id: UUID,
        workflow_step_id: UUID,
        actor: str | None,
        causality_reference: UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> OperationalEvent:
        return self.record(
            event_type=EVENT_BLOCKER_RESOLVED,
            aggregate_id=blocker_id,
            actor=actor,
            causality_reference=causality_reference,
            payload={
                "blocker_id": str(blocker_id),
                "workflow_step_id": str(workflow_step_id),
            },
            metadata=metadata,
        )


def _with_project(
    metadata: dict[str, Any] | None,
    project_id: UUID | None,
) -> dict[str, Any]:
    merged = dict(metadata or {})
    if project_id is not None:
        merged.setdefault("project_id", str(project_id))
    return merged


def _jsonable(value: dict[str, Any]) -> dict[str, Any]:
    """Best-effort coercion of UUID/Decimal/datetime to JSON-safe primitives."""
    return {key: _coerce(item) for key, item in value.items()}


def _coerce(item: Any) -> Any:
    if isinstance(item, (UUID, Decimal)):
        return str(item)
    if isinstance(item, datetime):
        return item.isoformat()
    if isinstance(item, dict):
        return _jsonable(item)
    if isinstance(item, (list, tuple)):
        return [_coerce(element) for element in item]
    return item
