from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    Boolean,
)
from datetime import datetime
import json

from backend.models.main_models import Base


class ValidationRule(Base):
    __tablename__ = "validation_rules"

    id = Column(Integer, primary_key=True)
    rule_id = Column(String(80), unique=True, nullable=False)
    name = Column(String(160), nullable=False)
    target = Column(String(60), nullable=False)
    severity_default = Column(String(20))
    description = Column(Text)
    is_active = Column(Boolean, default=True)


class ValidationResult(Base):
    __tablename__ = "validation_results"

    id = Column(Integer, primary_key=True)
    entity_type = Column(String(60), nullable=False)
    entity_id = Column(Integer, nullable=False)
    trust_score = Column(Float, nullable=False)
    validation_score = Column(Float, nullable=False)
    consistency_score = Column(Float, nullable=False)
    status = Column(String(20), nullable=False)
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class ValidationEvent(Base):
    __tablename__ = "validation_events"

    id = Column(Integer, primary_key=True)
    validation_result_id = Column(
        Integer,
        nullable=False,
    )
    rule_id = Column(String(80), nullable=False)
    target = Column(String(60), nullable=False)
    severity = Column(String(20), nullable=False)
    passed = Column(Boolean, nullable=False)
    message = Column(Text)
    explanation = Column(Text)
    confidence = Column(Float)
    affected_entities = Column(Text)
    operational_impact = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def serialize_entities(data: dict) -> str:
        return json.dumps(data or {})


class OperationalAnomaly(Base):
    __tablename__ = "operational_anomalies"

    id = Column(Integer, primary_key=True)
    validation_result_id = Column(Integer)
    entity_type = Column(String(60), nullable=False)
    entity_id = Column(Integer, nullable=False)
    anomaly_type = Column(String(80), nullable=False)
    target = Column(String(60))
    severity = Column(String(20), nullable=False)
    confidence = Column(Float)
    explanation = Column(Text)
    operational_impact = Column(Text)
    affected_entities = Column(Text)
    resolved = Column(Boolean, default=False)
    detected_at = Column(DateTime, default=datetime.utcnow)


class TrustScore(Base):
    __tablename__ = "trust_scores"

    id = Column(Integer, primary_key=True)
    entity_type = Column(String(60), nullable=False)
    entity_id = Column(Integer, nullable=False)
    score_type = Column(String(60), nullable=False)
    score = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    source = Column(String(60), default="validation_engine")


class ReportConsistency(Base):
    __tablename__ = "report_consistency"

    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, nullable=False, unique=True)
    consistency_score = Column(Float, nullable=False)
    quantity_deviation = Column(Float)
    manpower_deviation = Column(Float)
    delay_pattern_flag = Column(Boolean, default=False)
    metrics = Column(Text)
    recorded_at = Column(DateTime, default=datetime.utcnow)


class WorkforceReliability(Base):
    __tablename__ = "workforce_reliability"

    id = Column(Integer, primary_key=True)
    worker_identifier = Column(String(120), nullable=False)
    reporting_reliability = Column(Float, default=50)
    operational_consistency = Column(Float, default=50)
    attendance_trustworthiness = Column(Float, default=50)
    last_updated = Column(DateTime, default=datetime.utcnow)
