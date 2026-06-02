"""Blocker ORM model (Operational Constraint Layer)."""

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


class Blocker(Base):
    __tablename__ = "blockers"
    __table_args__ = (
        CheckConstraint(
            "blocker_type IN ("
            "'WEATHER', "
            "'EQUIPMENT', "
            "'MATERIAL', "
            "'WORKFORCE', "
            "'SITE_CONDITION', "
            "'EXTERNAL'"
            ")",
            name="blockers_blocker_type_check",
        ),
        CheckConstraint(
            "severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')",
            name="blockers_severity_check",
        ),
        CheckConstraint(
            "status IN ("
            "'OPEN', "
            "'ACKNOWLEDGED', "
            "'MITIGATION_IN_PROGRESS', "
            "'RESOLVED', "
            "'CLOSED', "
            "'REOPENED'"
            ")",
            name="blockers_status_check",
        ),
        Index("idx_blockers_workflow_step_id", "workflow_step_id"),
        Index("idx_blockers_status", "status"),
        Index("idx_blockers_detected_date", "detected_date"),
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
            name="blockers_workflow_step_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    blocker_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    detected_date: Mapped[date] = mapped_column(Date, nullable=False)
    resolved_date: Mapped[date | None] = mapped_column(Date)
    reported_by: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    root_cause: Mapped[str | None] = mapped_column(Text)
    resolution_notes: Mapped[str | None] = mapped_column(Text)
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
