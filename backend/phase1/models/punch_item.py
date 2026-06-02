"""PunchItem ORM model (Quality Layer)."""

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
    from backend.phase1.models.inspection import Inspection
    from backend.phase1.models.workflow_step import WorkflowStep


class PunchItem(Base):
    __tablename__ = "punch_items"
    __table_args__ = (
        CheckConstraint(
            "severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')",
            name="punch_items_severity_check",
        ),
        CheckConstraint(
            "status IN ("
            "'OPEN', "
            "'ASSIGNED', "
            "'IN_PROGRESS', "
            "'RESOLVED', "
            "'VERIFIED', "
            "'CLOSED', "
            "'REOPENED'"
            ")",
            name="punch_items_status_check",
        ),
        Index("idx_punch_items_workflow_step_id", "workflow_step_id"),
        Index("idx_punch_items_inspection_id", "inspection_id"),
        Index("idx_punch_items_status", "status"),
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
            name="punch_items_workflow_step_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    inspection_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "inspections.id",
            name="punch_items_inspection_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    assigned_to: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    due_date: Mapped[date | None] = mapped_column(Date)
    resolution_notes: Mapped[str | None] = mapped_column(Text)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
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
    inspection: Mapped[Inspection] = relationship(back_populates="punch_items")
