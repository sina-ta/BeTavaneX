"""WorkflowStep transport schemas (Pydantic v2). Contracts only; no logic."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WorkflowStepCreate(BaseModel):
    activity_instance_id: UUID
    workflow_template_id: UUID | None = None
    code: str
    name: str
    status: str
    ready: bool = False
    progress_percent: Decimal = Decimal("0")
    planned_weight: Decimal | None = None
    planned_start: date | None = None
    planned_finish: date | None = None
    actual_start: date | None = None
    actual_finish: date | None = None


class WorkflowStepUpdate(BaseModel):
    activity_instance_id: UUID | None = None
    workflow_template_id: UUID | None = None
    code: str | None = None
    name: str | None = None
    status: str | None = None
    ready: bool | None = None
    progress_percent: Decimal | None = None
    planned_weight: Decimal | None = None
    planned_start: date | None = None
    planned_finish: date | None = None
    actual_start: date | None = None
    actual_finish: date | None = None


class WorkflowStepRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    activity_instance_id: UUID
    workflow_template_id: UUID | None
    code: str
    name: str
    status: str
    ready: bool
    progress_percent: Decimal
    planned_weight: Decimal | None
    planned_start: date | None
    planned_finish: date | None
    actual_start: date | None
    actual_finish: date | None
    created_at: datetime
    updated_at: datetime
