"""Explainable operational intelligence responses (Stage 28)."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

HealthBand = Literal["GOOD", "ATTENTION", "AT_RISK", "UNKNOWN"]
SignalSeverity = Literal["info", "warning", "critical"]
Confidence = Literal["low", "medium", "high"]


class HealthComponentRead(BaseModel):
    factor: str
    impact: int = Field(description="Points subtracted from 100 (0 if none)")
    detail: str


class ProjectHealthRead(BaseModel):
    score: int | None = Field(None, ge=0, le=100)
    band: HealthBand
    components: list[HealthComponentRead] = Field(default_factory=list)
    summary: str


class AttentionItemRead(BaseModel):
    severity: SignalSeverity
    category: str
    message: str
    resource_type: str | None = None
    resource_id: UUID | None = None
    workflow_step_id: UUID | None = None


class OperationalSignalRead(BaseModel):
    signal_type: str
    severity: SignalSeverity
    message: str
    evidence: str
    count: int = 0


class PredictiveSignalRead(BaseModel):
    forecast: str
    confidence: Confidence
    reason: str
    workflow_step_id: UUID | None = None


class PriorityItemRead(BaseModel):
    rank: int
    category: str
    priority_score: int = Field(ge=0, le=100)
    severity: SignalSeverity
    title: str
    explanation: str
    resource_type: str | None = None
    resource_id: UUID | None = None
    workflow_step_id: UUID | None = None
    suggested_action: str


class ApprovalQueueItemRead(BaseModel):
    queue_position: int
    approval_id: UUID
    workflow_step_id: UUID
    step_code: str
    activity_code: str
    approval_type: str
    status: str
    days_pending: int
    overdue: bool
    priority_score: int
    explanation: str
    suggested_action: str


class OperationalRecommendationRead(BaseModel):
    severity: SignalSeverity
    message: str
    rationale: str


class WorkloadImbalanceRead(BaseModel):
    imbalance_type: str
    severity: SignalSeverity
    message: str
    evidence: str
    metric: int = 0


CoordinationBand = Literal["ALIGNED", "FRAGMENTED", "STRESSED", "UNKNOWN"]


class CrossRoleDependencyRead(BaseModel):
    from_role: str
    to_role: str
    dependency_type: str
    severity: SignalSeverity
    message: str
    evidence: str


class HandoffRiskRead(BaseModel):
    handoff_type: str
    severity: SignalSeverity
    message: str
    workflow_step_id: UUID | None = None
    context: str


class TeamExecutionFlowRead(BaseModel):
    reports_last_7_days: int = 0
    approvals_last_7_days: int = 0
    assignments_last_7_days: int = 0
    open_coordination_dependencies: int = 0
    coordination_density: float = 0
    supervisor_responsiveness_ratio: float = 0
    workflow_step_count: int = 0
    activity_count: int = 0


class CoordinationAttentionRead(BaseModel):
    severity: SignalSeverity
    category: str
    message: str
    workflow_step_id: UUID | None = None


class OperationalCoordinationIntelligenceRead(BaseModel):
    project_id: UUID
    generated_at: str
    data_available: bool
    coordination_band: CoordinationBand
    coordination_score: int | None = Field(None, ge=0, le=100)
    coordination_summary: str
    bottlenecks: list[OperationalSignalRead] = Field(default_factory=list)
    cross_role_dependencies: list[CrossRoleDependencyRead] = Field(default_factory=list)
    synchronization: list[OperationalSignalRead] = Field(default_factory=list)
    handoff_risks: list[HandoffRiskRead] = Field(default_factory=list)
    communication_gaps: list[OperationalSignalRead] = Field(default_factory=list)
    team_execution_flow: TeamExecutionFlowRead = Field(
        default_factory=TeamExecutionFlowRead,
    )
    coordination_attention: list[CoordinationAttentionRead] = Field(default_factory=list)
    worker_relevance: list[str] = Field(default_factory=list)
    false_positive_notes: list[str] = Field(default_factory=list)


class OperationalDecisionSupportRead(BaseModel):
    project_id: UUID
    generated_at: str
    data_available: bool
    priority_queue: list[PriorityItemRead] = Field(default_factory=list)
    supervisor_guidance: list[str] = Field(default_factory=list)
    approval_queue: list[ApprovalQueueItemRead] = Field(default_factory=list)
    blocker_guidance: list[OperationalSignalRead] = Field(default_factory=list)
    workload_imbalance: list[WorkloadImbalanceRead] = Field(default_factory=list)
    recommendations: list[OperationalRecommendationRead] = Field(default_factory=list)
    false_positive_notes: list[str] = Field(default_factory=list)


class OperationalIntelligenceRead(BaseModel):
    project_id: UUID
    generated_at: str
    data_available: bool
    stall_threshold_days: int
    approval_delay_threshold_days: int
    health: ProjectHealthRead
    stagnation: list[OperationalSignalRead] = Field(default_factory=list)
    approval_delays: list[OperationalSignalRead] = Field(default_factory=list)
    blocker_trends: list[OperationalSignalRead] = Field(default_factory=list)
    anomalies: list[OperationalSignalRead] = Field(default_factory=list)
    attention_needed: list[AttentionItemRead] = Field(default_factory=list)
    predictions: list[PredictiveSignalRead] = Field(default_factory=list)
    false_positive_notes: list[str] = Field(default_factory=list)
    decision_support: OperationalDecisionSupportRead | None = None
    coordination_intelligence: OperationalCoordinationIntelligenceRead | None = None
