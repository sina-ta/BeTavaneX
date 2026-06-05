"""Read-only derived readiness inspection schemas (Runtime Hardening P2)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ReadinessConditionRead(BaseModel):
    factor: str
    state: str
    detail: str
    evidence_source: str


class ReadinessContradictionRead(BaseModel):
    contradiction_type: str
    message: str
    evidence: str


class ReadinessInterpretationRead(BaseModel):
    workflow_step_id: str
    project_id: str
    derived_ready: bool
    stored_ready: bool
    interpretation_summary: str
    contributing_conditions: list[ReadinessConditionRead] = Field(default_factory=list)
    blocking_conditions: list[ReadinessConditionRead] = Field(default_factory=list)
    contradictions: list[ReadinessContradictionRead] = Field(default_factory=list)
    evidence_sources: list[str] = Field(default_factory=list)
    evaluated_at: str
    lineage_owner: str = "readiness_derivation_service"


class ReadinessLineageRead(BaseModel):
    event_id: str
    event_type: str
    occurred_at: str
    actor: str
    payload: dict
