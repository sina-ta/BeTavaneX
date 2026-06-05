"""Pure derived readiness evaluation (no orchestration, no scoring)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from backend.phase1.dependency_edges.taxonomy import (
    DEPENDENCY_EXECUTION,
    DEPENDENCY_GOVERNANCE,
    DEPENDENCY_READINESS,
    DEPENDENCY_RESOURCE,
    ENTITY_ACTIVITY_INSTANCE,
    ENTITY_WORKFLOW_STEP,
)

_OPEN_BLOCKER_STATUSES = frozenset(
    {"OPEN", "ACKNOWLEDGED", "MITIGATION_IN_PROGRESS", "REOPENED"},
)
_SOURCE_SATISFIED_STEP = frozenset({"COMPLETED", "APPROVED"})
_EXECUTABLE_STEP_STATUSES = frozenset(
    {"PLANNED", "IN_PROGRESS", "REWORK_REQUIRED", "INSPECTION_PENDING"},
)
_GOVERNANCE_SOURCE_REQUIRED = frozenset({"APPROVED"})


@dataclass(frozen=True, slots=True)
class ReadinessCondition:
    factor: str
    state: str
    detail: str
    evidence_source: str


@dataclass(frozen=True, slots=True)
class ReadinessContradiction:
    contradiction_type: str
    message: str
    evidence: str


@dataclass
class ReadinessDerivationResult:
    workflow_step_id: UUID
    project_id: UUID
    derived_ready: bool
    stored_ready: bool
    interpretation_summary: str
    contributing_conditions: list[ReadinessCondition] = field(default_factory=list)
    blocking_conditions: list[ReadinessCondition] = field(default_factory=list)
    contradictions: list[ReadinessContradiction] = field(default_factory=list)
    evidence_sources: list[str] = field(default_factory=list)
    evaluated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_step_id": str(self.workflow_step_id),
            "project_id": str(self.project_id),
            "derived_ready": self.derived_ready,
            "stored_ready": self.stored_ready,
            "interpretation_summary": self.interpretation_summary,
            "contributing_conditions": [
                {
                    "factor": c.factor,
                    "state": c.state,
                    "detail": c.detail,
                    "evidence_source": c.evidence_source,
                }
                for c in self.contributing_conditions
            ],
            "blocking_conditions": [
                {
                    "factor": c.factor,
                    "state": c.state,
                    "detail": c.detail,
                    "evidence_source": c.evidence_source,
                }
                for c in self.blocking_conditions
            ],
            "contradictions": [
                {
                    "contradiction_type": c.contradiction_type,
                    "message": c.message,
                    "evidence": c.evidence,
                }
                for c in self.contradictions
            ],
            "evidence_sources": list(self.evidence_sources),
            "evaluated_at": self.evaluated_at.isoformat(),
            "lineage_owner": "readiness_derivation_service",
        }


@dataclass(frozen=True, slots=True)
class _BlockerSnapshot:
    id: UUID
    title: str
    severity: str
    status: str


@dataclass(frozen=True, slots=True)
class _EdgeSnapshot:
    id: UUID
    dependency_type: str
    source_entity_type: str
    source_entity_id: UUID
    authority_level: str


@dataclass(frozen=True, slots=True)
class _StepSnapshot:
    id: UUID
    status: str
    ready: bool
    code: str


@dataclass(frozen=True, slots=True)
class _ActivitySnapshot:
    id: UUID
    status: str
    code: str


def derive_workflow_step_readiness(
    *,
    project_id: UUID,
    step: _StepSnapshot,
    blockers: list[_BlockerSnapshot],
    incoming_edges: list[_EdgeSnapshot],
    source_steps: dict[UUID, _StepSnapshot],
    source_activities: dict[UUID, _ActivitySnapshot],
) -> ReadinessDerivationResult:
    """Evaluate readiness as an explainable operational interpretation."""
    contributing: list[ReadinessCondition] = []
    blocking: list[ReadinessCondition] = []
    contradictions: list[ReadinessContradiction] = []
    evidence: set[str] = {"workflow_status"}

    if step.status in _SOURCE_SATISFIED_STEP:
        derived = False
        blocking.append(
            ReadinessCondition(
                factor="workflow_terminal_status",
                state="unsatisfied",
                detail=f"Step status {step.status} — execution already completed.",
                evidence_source="workflow_status",
            ),
        )
    elif step.status not in _EXECUTABLE_STEP_STATUSES:
        derived = False
        blocking.append(
            ReadinessCondition(
                factor="workflow_status",
                state="unsatisfied",
                detail=f"Step status {step.status} is not in an executable band.",
                evidence_source="workflow_status",
            ),
        )
    else:
        derived = True
        contributing.append(
            ReadinessCondition(
                factor="workflow_status",
                state="satisfied",
                detail=f"Step status {step.status} permits execution consideration.",
                evidence_source="workflow_status",
            ),
        )

    open_blockers = [b for b in blockers if b.status in _OPEN_BLOCKER_STATUSES]
    if open_blockers:
        evidence.add("blocker")
        derived = False
        for blocker in open_blockers:
            blocking.append(
                ReadinessCondition(
                    factor="open_blocker",
                    state="unsatisfied",
                    detail=f"{blocker.title} ({blocker.severity}, {blocker.status})",
                    evidence_source="blocker",
                ),
            )

    for edge in incoming_edges:
        evidence.add("dependency_edge")
        satisfied, detail = _evaluate_incoming_edge(
            edge,
            source_steps=source_steps,
            source_activities=source_activities,
        )
        condition = ReadinessCondition(
            factor=f"incoming_{edge.dependency_type}",
            state="satisfied" if satisfied else "unsatisfied",
            detail=detail,
            evidence_source="dependency_edge",
        )
        if satisfied:
            contributing.append(condition)
        else:
            blocking.append(condition)
            if edge.dependency_type in (
                DEPENDENCY_EXECUTION,
                DEPENDENCY_READINESS,
                DEPENDENCY_GOVERNANCE,
            ):
                derived = False
            elif edge.dependency_type == DEPENDENCY_RESOURCE:
                derived = False

    if step.ready != derived:
        evidence.add("stored_ready_column")
        contradictions.append(
            ReadinessContradiction(
                contradiction_type="stored_vs_derived",
                message=(
                    f"Stored ready={step.ready} contradicts derived ready={derived}."
                ),
                evidence="workflow_steps.ready vs ReadinessDerivationService",
            ),
        )
    if step.ready and open_blockers:
        contradictions.append(
            ReadinessContradiction(
                contradiction_type="ready_with_open_blockers",
                message="Stored ready=true while open blockers exist on this step.",
                evidence="blocker + workflow_steps.ready",
            ),
        )

    summary = _build_summary(derived, blocking, contradictions)

    return ReadinessDerivationResult(
        workflow_step_id=step.id,
        project_id=project_id,
        derived_ready=derived,
        stored_ready=step.ready,
        interpretation_summary=summary,
        contributing_conditions=contributing,
        blocking_conditions=blocking,
        contradictions=contradictions,
        evidence_sources=sorted(evidence),
    )


def _evaluate_incoming_edge(
    edge: _EdgeSnapshot,
    *,
    source_steps: dict[UUID, _StepSnapshot],
    source_activities: dict[UUID, _ActivitySnapshot],
) -> tuple[bool, str]:
    if edge.source_entity_type == ENTITY_WORKFLOW_STEP:
        source = source_steps.get(edge.source_entity_id)
        if source is None:
            return False, f"Source workflow step {edge.source_entity_id} not found."
        if edge.dependency_type == DEPENDENCY_GOVERNANCE:
            ok = source.status in _GOVERNANCE_SOURCE_REQUIRED
            return (
                ok,
                f"Governance dependency: source {source.code} status {source.status} "
                f"{'meets' if ok else 'does not meet'} APPROVED requirement.",
            )
        if edge.dependency_type in (DEPENDENCY_EXECUTION, DEPENDENCY_READINESS):
            ok = source.status in _SOURCE_SATISFIED_STEP
            return (
                ok,
                f"{edge.dependency_type}: source {source.code} status {source.status} "
                f"{'satisfies' if ok else 'does not satisfy'} predecessor completion.",
            )
        if edge.dependency_type == DEPENDENCY_RESOURCE:
            ok = source.status in _SOURCE_SATISFIED_STEP
            return (
                ok,
                f"Resource dependency: source {source.code} status {source.status} "
                f"({'available' if ok else 'constraint unresolved'}).",
            )
        return True, f"Incoming {edge.dependency_type} edge recorded (advisory)."

    if edge.source_entity_type == ENTITY_ACTIVITY_INSTANCE:
        source = source_activities.get(edge.source_entity_id)
        if source is None:
            return False, f"Source activity {edge.source_entity_id} not found."
        ok = source.status == "COMPLETED"
        return (
            ok,
            f"{edge.dependency_type}: source activity {source.code} status "
            f"{source.status} {'satisfies' if ok else 'does not satisfy'} completion.",
        )

    return True, f"Incoming edge from {edge.source_entity_type} (no step rule)."


def _build_summary(
    derived: bool,
    blocking: list[ReadinessCondition],
    contradictions: list[ReadinessContradiction],
) -> str:
    if contradictions:
        return (
            "Readiness interpretation has unresolved contradictions — "
            "review blocking conditions before execution proceeds."
        )
    if derived:
        return (
            "Derived readiness: execution may operationally proceed "
            "(advisory — no automatic orchestration)."
        )
    if blocking:
        primary = blocking[0].detail
        return f"Derived readiness: not ready — {primary}"
    return "Derived readiness: not ready — insufficient operational evidence."
