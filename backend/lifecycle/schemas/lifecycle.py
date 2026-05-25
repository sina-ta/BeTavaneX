from pydantic import BaseModel
from typing import Optional


class TaskTransitionRequest(BaseModel):
    to_state: str
    triggered_by: Optional[str] = None
    reason: Optional[str] = None


class BlockerCreateRequest(BaseModel):
    entity_type: str
    entity_id: int
    blocker_type: str
    title: str
    severity: str = "medium"
    description: Optional[str] = None
    operational_impact: Optional[str] = None
    expected_delay_days: Optional[float] = None
    responsible_entity: Optional[str] = None
    task_id: Optional[int] = None
    work_order_id: Optional[int] = None


class ApprovalRequestPayload(BaseModel):
    entity_type: str
    entity_id: int
    requested_by: str


class ApprovalDecisionPayload(BaseModel):
    role: str
    decision: str
    decided_by: str
    notes: Optional[str] = None
