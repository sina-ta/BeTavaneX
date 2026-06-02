"""Inspection ORM model (Quality Layer)."""

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
    from backend.phase1.models.punch_item import PunchItem
    from backend.phase1.models.workflow_step import WorkflowStep


class Inspection(Base):
    __tablename__ = "inspections"
    __table_args__ = (
        CheckConstraint(
            "status IN ('CREATED', 'SCHEDULED', 'IN_PROGRESS', 'PASSED', 'FAILED')",
            name="inspections_status_check",
        ),
        CheckConstraint(
            "result IN ('PASS', 'FAIL')",
            name="inspections_result_check",
        ),
        Index("idx_inspections_workflow_step_id", "workflow_step_id"),
        Index("idx_inspections_inspection_date", "inspection_date"),
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
            name="inspections_workflow_step_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    inspection_type: Mapped[str] = mapped_column(String(100), nullable=False)
    inspection_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    inspector_name: Mapped[str | None] = mapped_column(String(255))
    inspection_notes: Mapped[str | None] = mapped_column(Text)
    result: Mapped[str] = mapped_column(String(50), nullable=False)
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
    punch_items: Mapped[list["PunchItem"]] = relationship(
        back_populates="inspection",
    )
