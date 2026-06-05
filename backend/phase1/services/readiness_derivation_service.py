"""Derived readiness ownership service (Runtime Hardening P2).

Evaluates readiness from operational evidence, owns synchronization of the
``workflow_steps.ready`` cache column, and records lineage events. Does not
schedule, propagate, or orchestrate execution.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from backend.phase1.dependency_edges.taxonomy import ENTITY_WORKFLOW_STEP
from backend.phase1.events.event_recording_service import EventRecordingService
from backend.phase1.events.taxonomy import (
    EVENT_READINESS_BLOCKED,
    EVENT_READINESS_EVALUATED,
    EVENT_READINESS_RECOVERED,
)
from backend.phase1.models.operational_event import OperationalEvent
from backend.phase1.readiness.derivation import (
    ReadinessDerivationResult,
    _ActivitySnapshot,
    _BlockerSnapshot,
    _EdgeSnapshot,
    _StepSnapshot,
    derive_workflow_step_readiness,
)
from backend.phase1.repositories.activity_instance_repository import (
    ActivityInstanceRepository,
)
from backend.phase1.repositories.blocker_repository import BlockerRepository
from backend.phase1.repositories.operational_dependency_edge_repository import (
    OperationalDependencyEdgeRepository,
)
from backend.phase1.repositories.operational_event_repository import (
    OperationalEventRepository,
)
from backend.phase1.repositories.workflow_step_repository import WorkflowStepRepository


class ReadinessDerivationService:
    """Single owner of derived readiness interpretation for workflow steps."""

    def __init__(
        self,
        workflow_step_repository: WorkflowStepRepository,
        activity_instance_repository: ActivityInstanceRepository,
        blocker_repository: BlockerRepository,
        edge_repository: OperationalDependencyEdgeRepository,
        event_recorder: EventRecordingService | None = None,
        event_repository: OperationalEventRepository | None = None,
    ) -> None:
        self._steps = workflow_step_repository
        self._activities = activity_instance_repository
        self._blockers = blocker_repository
        self._edges = edge_repository
        self._event_recorder = event_recorder
        self._event_repository = event_repository

    def inspect_workflow_step(
        self,
        workflow_step_id: UUID,
        project_id: UUID,
    ) -> ReadinessDerivationResult:
        """Read-only derived readiness interpretation (no persistence)."""
        return self._evaluate(workflow_step_id, project_id)

    def initialize_workflow_step(
        self,
        workflow_step_id: UUID,
        project_id: UUID,
        *,
        actor: str | None,
        trigger: str = "workflow_step_created",
    ) -> ReadinessDerivationResult:
        """Derive and persist readiness for a newly created step."""
        return self._refresh(
            workflow_step_id,
            project_id,
            actor=actor,
            trigger=trigger,
            prior_ready=False,
        )

    def refresh_workflow_step(
        self,
        workflow_step_id: UUID,
        project_id: UUID,
        *,
        actor: str | None,
        trigger: str,
        causality_reference: UUID | None = None,
    ) -> ReadinessDerivationResult:
        """Re-derive readiness after an operational change."""
        step = self._require_step(workflow_step_id)
        return self._refresh(
            workflow_step_id,
            project_id,
            actor=actor,
            trigger=trigger,
            prior_ready=step.ready,
            causality_reference=causality_reference,
        )

    def refresh_for_workflow_step(
        self,
        workflow_step_id: UUID,
        *,
        actor: str | None,
        trigger: str,
        causality_reference: UUID | None = None,
    ) -> ReadinessDerivationResult | None:
        """Resolve project scope and refresh readiness (chokepoint helper)."""
        step = self._require_step(workflow_step_id)
        activity = self._activities.get_by_id(step.activity_instance_id)
        if activity is None:
            return None
        return self.refresh_workflow_step(
            workflow_step_id,
            activity.project_id,
            actor=actor,
            trigger=trigger,
            causality_reference=causality_reference,
        )

    def list_lineage(
        self,
        workflow_step_id: UUID,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[OperationalEvent]:
        if self._event_repository is None:
            return []
        events = self._event_repository.list_for_aggregate(
            "workflow_step",
            workflow_step_id,
            offset=offset,
            limit=limit,
        )
        readiness_types = {
            EVENT_READINESS_EVALUATED,
            EVENT_READINESS_BLOCKED,
            EVENT_READINESS_RECOVERED,
        }
        return [event for event in events if event.event_type in readiness_types]

    def _refresh(
        self,
        workflow_step_id: UUID,
        project_id: UUID,
        *,
        actor: str | None,
        trigger: str,
        prior_ready: bool,
        causality_reference: UUID | None = None,
    ) -> ReadinessDerivationResult:
        result = self._evaluate(workflow_step_id, project_id)
        step = self._require_step(workflow_step_id)

        if step.ready != result.derived_ready:
            step.ready = result.derived_ready
            self._steps.update(step, resource_type="WorkflowStep")

        if self._event_recorder is not None:
            payload = result.to_dict()
            payload["trigger"] = trigger
            self._record_lineage_transition(
                workflow_step_id=workflow_step_id,
                project_id=project_id,
                actor=actor,
                prior_ready=prior_ready,
                derived_ready=result.derived_ready,
                payload=payload,
                causality_reference=causality_reference,
            )

        return result

    def _record_lineage_transition(
        self,
        *,
        workflow_step_id: UUID,
        project_id: UUID,
        actor: str | None,
        prior_ready: bool,
        derived_ready: bool,
        payload: dict[str, Any],
        causality_reference: UUID | None,
    ) -> None:
        assert self._event_recorder is not None
        metadata = {"project_id": str(project_id), "trigger": payload.get("trigger")}

        if not prior_ready and derived_ready:
            self._event_recorder.record_readiness_recovered(
                workflow_step_id=workflow_step_id,
                actor=actor,
                payload=payload,
                causality_reference=causality_reference,
                project_id=project_id,
            )
        elif prior_ready and not derived_ready:
            self._event_recorder.record_readiness_blocked(
                workflow_step_id=workflow_step_id,
                actor=actor,
                payload=payload,
                causality_reference=causality_reference,
                project_id=project_id,
            )
        else:
            self._event_recorder.record_readiness_evaluated(
                workflow_step_id=workflow_step_id,
                actor=actor,
                payload=payload,
                causality_reference=causality_reference,
                project_id=project_id,
            )

    def _evaluate(
        self,
        workflow_step_id: UUID,
        project_id: UUID,
    ) -> ReadinessDerivationResult:
        step = self._require_step(workflow_step_id)
        activity = self._activities.get_by_id(step.activity_instance_id)
        if activity is None:
            msg = f"ActivityInstance not found for step {workflow_step_id}"
            raise ValueError(msg)
        if activity.project_id != project_id:
            msg = (
                f"Workflow step {workflow_step_id} does not belong to "
                f"project {project_id}"
            )
            raise ValueError(msg)

        blockers = self._blockers.list(workflow_step_id=workflow_step_id)
        _, incoming = self._edges.trace_entity(
            project_id,
            entity_type=ENTITY_WORKFLOW_STEP,
            entity_id=workflow_step_id,
        )

        source_step_ids = [
            edge.source_entity_id
            for edge in incoming
            if edge.source_entity_type == ENTITY_WORKFLOW_STEP
        ]
        source_steps: dict[UUID, _StepSnapshot] = {}
        for sid in source_step_ids:
            source = self._steps.get_by_id(sid)
            if source is not None:
                source_steps[sid] = _StepSnapshot(
                    id=source.id,
                    status=source.status,
                    ready=source.ready,
                    code=source.code,
                )

        source_activity_ids = [
            edge.source_entity_id
            for edge in incoming
            if edge.source_entity_type == "activity_instance"
        ]
        source_activities: dict[UUID, _ActivitySnapshot] = {}
        for aid in source_activity_ids:
            src_activity = self._activities.get_by_id(aid)
            if src_activity is not None:
                source_activities[aid] = _ActivitySnapshot(
                    id=src_activity.id,
                    status=src_activity.status,
                    code=src_activity.code,
                )

        return derive_workflow_step_readiness(
            project_id=project_id,
            step=_StepSnapshot(
                id=step.id,
                status=step.status,
                ready=step.ready,
                code=step.code,
            ),
            blockers=[
                _BlockerSnapshot(
                    id=b.id,
                    title=b.title,
                    severity=b.severity,
                    status=b.status,
                )
                for b in blockers
            ],
            incoming_edges=[
                _EdgeSnapshot(
                    id=edge.id,
                    dependency_type=edge.dependency_type,
                    source_entity_type=edge.source_entity_type,
                    source_entity_id=edge.source_entity_id,
                    authority_level=edge.authority_level,
                )
                for edge in incoming
            ],
            source_steps=source_steps,
            source_activities=source_activities,
        )

    def _require_step(self, workflow_step_id: UUID):
        step = self._steps.get_by_id(workflow_step_id)
        if step is None:
            msg = f"WorkflowStep not found: {workflow_step_id}"
            raise ValueError(msg)
        return step
