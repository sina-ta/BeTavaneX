"""Executive operational visibility responses (Stage 32)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from backend.phase1.schemas.operational_intelligence_schema import (
    OperationalSignalRead,
    SignalSeverity,
)

PortfolioBand = Literal["HEALTHY", "STABLE", "CAUTION", "CRITICAL", "UNKNOWN"]
AttentionLevel = Literal["immediate", "planned", "monitor", "stable"]


class PortfolioHealthRead(BaseModel):
    overall_band: PortfolioBand
    summary: str
    projects_analyzed: int = 0
    health_distribution: dict[str, int] = Field(default_factory=dict)
    coordination_pressure_distribution: dict[str, int] = Field(default_factory=dict)
    maturity_band: str = "UNKNOWN"
    capacity_band: str = "UNKNOWN"
    deteriorating_project_codes: list[str] = Field(default_factory=list)
    stable_project_codes: list[str] = Field(default_factory=list)


class TrendNarrativeRead(BaseModel):
    narrative_id: str
    trend_direction: Literal["improving", "stable", "worsening", "unknown"]
    message: str
    evidence: str


class LeadershipPriorityRead(BaseModel):
    rank: int = Field(ge=1, le=10)
    concern: str
    attention_level: AttentionLevel
    evidence: str
    suggested_focus: str


class PressureIndicatorRead(BaseModel):
    indicator_type: str
    severity: SignalSeverity
    message: str
    evidence: str


class ExecutiveVisibilityRead(BaseModel):
    generated_at: str
    data_available: bool
    executive_summary: str
    portfolio_health: PortfolioHealthRead
    strategic_risks: list[OperationalSignalRead] = Field(default_factory=list)
    trend_narratives: list[TrendNarrativeRead] = Field(default_factory=list)
    leadership_priorities: list[LeadershipPriorityRead] = Field(default_factory=list)
    pressure_indicators: list[PressureIndicatorRead] = Field(default_factory=list)
    strategic_attention: list[str] = Field(default_factory=list)
    false_positive_notes: list[str] = Field(default_factory=list)
