from pydantic import BaseModel
from typing import Any, Optional


class ValidationFindingSchema(BaseModel):
    rule_id: str
    target: str
    severity: str
    passed: bool
    message: str
    explanation: str
    confidence: float
    affected_entities: dict[str, Any] = {}
    operational_impact: str = ""


class ValidationPipelineResult(BaseModel):
    trusted: bool
    status: str
    trust_score: float
    validation_score: float
    consistency_score: float
    findings: list[ValidationFindingSchema]
    anomalies: list[dict[str, Any]]
    warnings: list[str]
    summary: str


class ValidationSummarySchema(BaseModel):
    total_validated: int
    trusted_count: int
    active_anomalies: int


class AnomalySchema(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    anomaly_type: str
    severity: str
    confidence: Optional[float] = None
    explanation: Optional[str] = None
    operational_impact: Optional[str] = None
