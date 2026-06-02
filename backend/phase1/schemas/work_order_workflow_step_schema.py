"""WorkOrderWorkflowStep (assignment) transport schemas (Pydantic v2)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WorkOrderAssignmentCreate(BaseModel):
    workflow_step_id: UUID
    execution_weight: Decimal


class WorkOrderWorkflowStepRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    work_order_id: UUID
    workflow_step_id: UUID
    execution_weight: Decimal
    created_at: datetime
