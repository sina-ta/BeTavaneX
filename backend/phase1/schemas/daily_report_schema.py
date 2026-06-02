"""DailyReport transport schemas (Pydantic v2). Contracts only; no logic."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DailyReportCreate(BaseModel):
    work_order_id: UUID
    report_date: date
    status: str = "DRAFT"
    summary: str | None = None
    execution_notes: str | None = None
    issue_notes: str | None = None
    delay_notes: str | None = None
    weather_notes: str | None = None
    evidence_metadata: dict[str, Any] | list[Any] | None = None
    submitted_by: UUID | None = None
    submitted_at: datetime | None = None
    reported_manpower: int | None = 0
    reported_equipment: int | None = 0
    reported_material_entries: int | None = 0


class DailyReportUpdate(BaseModel):
    work_order_id: UUID | None = None
    report_date: date | None = None
    status: str | None = None
    summary: str | None = None
    execution_notes: str | None = None
    issue_notes: str | None = None
    delay_notes: str | None = None
    weather_notes: str | None = None
    evidence_metadata: dict[str, Any] | list[Any] | None = None
    submitted_by: UUID | None = None
    submitted_at: datetime | None = None
    reported_manpower: int | None = None
    reported_equipment: int | None = None
    reported_material_entries: int | None = None


class DailyReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    work_order_id: UUID
    report_date: date
    status: str
    summary: str | None
    execution_notes: str | None
    issue_notes: str | None
    delay_notes: str | None
    weather_notes: str | None
    evidence_metadata: dict[str, Any] | list[Any] | None
    submitted_by: UUID | None
    submitted_at: datetime | None
    reported_manpower: int | None
    reported_equipment: int | None
    reported_material_entries: int | None
    created_at: datetime
    updated_at: datetime
