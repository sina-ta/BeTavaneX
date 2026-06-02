"""WBSItem transport schemas (Pydantic v2). Contracts only; no logic."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WBSItemCreate(BaseModel):
    project_id: UUID
    code: str
    name: str
    level: int
    parent_id: UUID | None = None
    description: str | None = None
    status: str = "ACTIVE"


class WBSItemUpdate(BaseModel):
    project_id: UUID | None = None
    code: str | None = None
    name: str | None = None
    level: int | None = None
    parent_id: UUID | None = None
    description: str | None = None
    status: str | None = None


class WBSItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    parent_id: UUID | None
    code: str
    name: str
    description: str | None
    level: int
    status: str
    created_at: datetime
    updated_at: datetime
