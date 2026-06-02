"""Approval ORM model (Quality Layer)."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base

if TYPE_CHECKING:
    from backend.phase1.models.workflow_step import WorkflowStep


class Approval(Base):
    __tablename__ = "approvals"
    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING', 'UNDER_REVIEW', 'APPROVED', 'REJECTED')",
            name="approvals_status_check",
        ),
        Index("idx_approvals_workflow_step_id", "workflow_step_id"),
        Index("idx_approvals_status", "status"),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    workflow_step_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "workflow_steps.id",
            name="approvals_workflow_step_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    approval_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        server_default="FINAL",
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    approval_date: Mapped[date | None] = mapped_column(Date)
    approved_by: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    approval_notes: Mapped[str | None] = mapped_column(Text)
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    workflow_step: Mapped[WorkflowStep] = relationship()
