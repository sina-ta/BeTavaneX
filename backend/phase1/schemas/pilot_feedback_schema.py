"""Pilot feedback capture (Stage 25 — operational validation, not a domain entity)."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

PilotFeedbackCategory = Literal[
    "confusion",
    "blocker",
    "missing_flow",
    "ux_pain",
    "gap",
    "other",
]


class PilotFeedbackCreate(BaseModel):
    category: PilotFeedbackCategory = "other"
    message: str = Field(..., min_length=3, max_length=4000)
    page_path: str | None = Field(None, max_length=500)
    project_id: UUID | None = None
