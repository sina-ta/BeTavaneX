"""Client usage events for live pilot adoption analytics (Stage 27)."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

UsageEventType = Literal["page_view", "session_start"]


class UsageEventCreate(BaseModel):
    event_type: UsageEventType = "page_view"
    page_path: str = Field(..., min_length=1, max_length=500)
    session_id: str | None = Field(None, max_length=64)
    referrer_path: str | None = Field(None, max_length=500)
    project_id: UUID | None = None
