"""Approval transport schemas (Pydantic v2). Contracts only; no logic."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WorkflowStepApprovalCreate(BaseModel):
    approval_type: str = "FINAL"
    approved_by: UUID | None = None
    approval_date: date | None = None
    approval_notes: str | None = None


class ApprovalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workflow_step_id: UUID
    approval_type: str
    status: str
    approval_date: date | None
    approved_by: UUID | None
    approval_notes: str | None
    rejection_reason: str | None
    created_at: datetime
    updated_at: datetime
