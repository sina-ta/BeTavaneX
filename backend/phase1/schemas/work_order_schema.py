"""WorkOrder transport schemas (Pydantic v2). Contracts only; no logic."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WorkOrderCreate(BaseModel):
    project_id: UUID
    work_order_number: str
    title: str
    description: str | None = None
    planned_date: date
    status: str = "CREATED"
    created_by: UUID | None = None


class WorkOrderUpdate(BaseModel):
    project_id: UUID | None = None
    work_order_number: str | None = None
    title: str | None = None
    description: str | None = None
    planned_date: date | None = None
    status: str | None = None
    created_by: UUID | None = None


class WorkOrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    work_order_number: str
    title: str
    description: str | None
    planned_date: date
    status: str
    created_by: UUID | None
    created_at: datetime
    updated_at: datetime
