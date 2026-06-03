"""Organizational execution intelligence responses (Stage 31)."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from backend.phase1.schemas.operational_intelligence_schema import (
    OperationalSignalRead,
    SignalSeverity,
)

MaturityBand = Literal["ESTABLISHED", "DEVELOPING", "EMERGING", "STRAINED", "UNKNOWN"]
CapacityBand = Literal["BALANCED", "PRESSURED", "SATURATED", "UNKNOWN"]


class MaturityComponentRead(BaseModel):
    factor: str
    score: int = Field(ge=0, le=100)
    detail: str


class ProjectExecutionSnapshotRead(BaseModel):
    project_id: UUID
    project_code: str
    project_name: str
    health_band: str
    coordination_pressure: str
    open_blockers: int = 0
    pending_approvals: int = 0
    reports_last_7_days: int = 0
    stalled_steps: int = 0


class SupervisorTrendRead(BaseModel):
    username: str
    role: str
    approvals_7d: int = 0
    assignments_7d: int = 0
    audit_actions_7d: int = 0
    observation: str
    concentration_risk: bool = False


class OrganizationalIntelligenceRead(BaseModel):
    generated_at: str
    data_available: bool
    projects_analyzed: int = 0
    maturity_band: MaturityBand
    maturity_score: int | None = Field(None, ge=0, le=100)
    maturity_summary: str
    maturity_components: list[MaturityComponentRead] = Field(default_factory=list)
    capacity_band: CapacityBand
    capacity_summary: str
    cross_project_findings: list[OperationalSignalRead] = Field(default_factory=list)
    organizational_bottlenecks: list[OperationalSignalRead] = Field(default_factory=list)
    supervisor_trends: list[SupervisorTrendRead] = Field(default_factory=list)
    culture_indicators: list[OperationalSignalRead] = Field(default_factory=list)
    multi_project_coordination: list[OperationalSignalRead] = Field(default_factory=list)
    project_snapshots: list[ProjectExecutionSnapshotRead] = Field(default_factory=list)
    organizational_attention: list[str] = Field(default_factory=list)
    false_positive_notes: list[str] = Field(default_factory=list)
