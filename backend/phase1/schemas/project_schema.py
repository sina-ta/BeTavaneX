"""Project transport schemas (Pydantic v2). Contracts only; no business logic."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    code: str
    name: str
    description: str | None = None
    status: str = "ACTIVE"
    planned_start: date | None = None
    planned_finish: date | None = None


class ProjectUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    description: str | None = None
    status: str | None = None
    planned_start: date | None = None
    planned_finish: date | None = None


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    description: str | None
    status: str
    planned_start: date | None
    planned_finish: date | None
    created_at: datetime
    updated_at: datetime
