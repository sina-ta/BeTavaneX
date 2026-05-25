from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    Boolean,
    DateTime,
)
from datetime import datetime
import json

from backend.models.main_models import Base


class TaskLifecycle(Base):
    __tablename__ = "lifecycle_task_states"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, nullable=False, unique=True, index=True)
    work_order_id = Column(Integer, index=True)
    current_state = Column(String(40), nullable=False, default="planned")
    maturity_level = Column(String(40), default="initial")
    responsible_entity = Column(String(120))
    operational_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class WorkOrderLifecycle(Base):
    __tablename__ = "lifecycle_work_order_states"

    id = Column(Integer, primary_key=True)
    work_order_id = Column(Integer, nullable=False, unique=True, index=True)
    task_id = Column(Integer, index=True)
    current_state = Column(String(40), nullable=False, default="created")
    responsible_entity = Column(String(120))
    approved_by = Column(String(120))
    approved_at = Column(DateTime)
    activated_at = Column(DateTime)
    completed_at = Column(DateTime)
    closed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class LifecycleTransition(Base):
    __tablename__ = "lifecycle_transitions"

    id = Column(Integer, primary_key=True)
    entity_type = Column(String(40), nullable=False)
    entity_id = Column(Integer, nullable=False)
    from_state = Column(String(40))
    to_state = Column(String(40), nullable=False)
    triggered_by = Column(String(120))
    reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class OperationalBlocker(Base):
    __tablename__ = "lifecycle_blockers"

    id = Column(Integer, primary_key=True)
    entity_type = Column(String(40), nullable=False)
    entity_id = Column(Integer, nullable=False)
    task_id = Column(Integer, index=True)
    work_order_id = Column(Integer, index=True)
    blocker_type = Column(String(40), nullable=False)
    severity = Column(String(20), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    operational_impact = Column(Text)
    expected_delay_days = Column(Float)
    responsible_entity = Column(String(120))
    resolution_state = Column(String(40), default="open")
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class ExecutionDependency(Base):
    __tablename__ = "lifecycle_dependencies"

    id = Column(Integer, primary_key=True)
    dependent_entity_type = Column(String(40), nullable=False)
    dependent_entity_id = Column(Integer, nullable=False)
    dependency_type = Column(String(40), nullable=False)
    depends_on_entity_type = Column(String(40))
    depends_on_entity_id = Column(Integer)
    is_satisfied = Column(Boolean, default=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class ApprovalRequest(Base):
    __tablename__ = "lifecycle_approvals"

    id = Column(Integer, primary_key=True)
    entity_type = Column(String(40), nullable=False)
    entity_id = Column(Integer, nullable=False)
    approval_chain_level = Column(Integer, default=1)
    required_role = Column(String(80), nullable=False)
    status = Column(String(40), default="pending")
    requested_by = Column(String(120))
    decided_by = Column(String(120))
    decision_notes = Column(Text)
    requested_at = Column(DateTime, default=datetime.utcnow)
    decided_at = Column(DateTime)


class EscalationRecord(Base):
    __tablename__ = "lifecycle_escalations"

    id = Column(Integer, primary_key=True)
    entity_type = Column(String(40), nullable=False)
    entity_id = Column(Integer, nullable=False)
    task_id = Column(Integer, index=True)
    work_order_id = Column(Integer, index=True)
    trigger_type = Column(String(60), nullable=False)
    escalation_level = Column(String(20), nullable=False)
    severity = Column(String(20), nullable=False)
    responsible_role = Column(String(80))
    operational_impact = Column(Text)
    resolution_state = Column(String(40), default="open")
    resolved_by = Column(String(120))
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class ExecutionReadiness(Base):
    __tablename__ = "lifecycle_readiness"

    id = Column(Integer, primary_key=True)
    entity_type = Column(String(40), nullable=False)
    entity_id = Column(Integer, nullable=False)
    task_id = Column(Integer, index=True)
    readiness_status = Column(String(40), nullable=False)
    readiness_score = Column(Float)
    factors = Column(Text)
    evaluated_at = Column(DateTime, default=datetime.utcnow)


class OperationalTimelineEvent(Base):
    __tablename__ = "lifecycle_timeline_events"

    id = Column(Integer, primary_key=True)
    entity_type = Column(String(40), nullable=False)
    entity_id = Column(Integer, nullable=False)
    task_id = Column(Integer, index=True)
    work_order_id = Column(Integer, index=True)
    event_type = Column(String(40), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    severity = Column(String(20))
    payload = Column(Text)
    recorded_by = Column(String(120))
    occurred_at = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def serialize_payload(data: dict) -> str:
        return json.dumps(data or {})
