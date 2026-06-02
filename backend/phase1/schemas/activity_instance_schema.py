"""ActivityInstance transport schemas (Pydantic v2). Contracts only; no logic."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ActivityInstanceCreate(BaseModel):
    project_id: UUID
    wbs_item_id: UUID
    location_id: UUID
    code: str
    name: str
    planned_start: date | None = None
    planned_finish: date | None = None
    planned_duration_days: int | None = None
    status: str = "ACTIVE"


class ActivityInstanceUpdate(BaseModel):
    project_id: UUID | None = None
    wbs_item_id: UUID | None = None
    location_id: UUID | None = None
    code: str | None = None
    name: str | None = None
    planned_start: date | None = None
    planned_finish: date | None = None
    planned_duration_days: int | None = None
    status: str | None = None


class ActivityInstanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    wbs_item_id: UUID
    location_id: UUID
    code: str
    name: str
    planned_start: date | None
    planned_finish: date | None
    planned_duration_days: int | None
    status: str
    created_at: datetime
    updated_at: datetime
