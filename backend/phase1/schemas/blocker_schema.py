"""Blocker transport schemas (Pydantic v2). Contracts only; no logic."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BlockerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workflow_step_id: UUID
    title: str
    description: str | None
    blocker_type: str
    severity: str
    status: str
    detected_date: date
    resolved_date: date | None
    reported_by: UUID | None
    root_cause: str | None
    resolution_notes: str | None
    created_at: datetime
    updated_at: datetime
