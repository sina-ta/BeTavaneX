"""WorkflowStep ORM model (Execution Reality Layer)."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base

if TYPE_CHECKING:
    from backend.phase1.models.activity_instance import ActivityInstance
    from backend.phase1.models.workflow_step_template import WorkflowStepTemplate


class WorkflowStep(Base):
    __tablename__ = "workflow_steps"
    __table_args__ = (
        UniqueConstraint(
            "activity_instance_id",
            "code",
            name="workflow_steps_activity_instance_id_code_key",
        ),
        CheckConstraint(
            "status IN ("
            "'PLANNED', "
            "'IN_PROGRESS', "
            "'COMPLETED', "
            "'INSPECTION_PENDING', "
            "'INSPECTION_FAILED', "
            "'REWORK_REQUIRED', "
            "'APPROVED'"
            ")",
            name="workflow_steps_status_check",
        ),
        CheckConstraint(
            "progress_percent >= 0 AND progress_percent <= 100",
            name="workflow_steps_progress_percent_range_check",
        ),
        CheckConstraint(
            "planned_weight IS NULL OR "
            "(planned_weight >= 0 AND planned_weight <= 100)",
            name="workflow_steps_planned_weight_range_check",
        ),
        Index("idx_workflow_steps_activity_instance_id", "activity_instance_id"),
        Index("idx_workflow_steps_workflow_template_id", "workflow_template_id"),
        Index("idx_workflow_steps_status", "status"),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    activity_instance_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "activity_instances.id",
            name="workflow_steps_activity_instance_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    workflow_template_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "workflow_step_templates.id",
            name="workflow_steps_workflow_template_id_fkey",
            ondelete="RESTRICT",
        ),
    )
    code: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    ready: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    progress_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        server_default=text("0"),
    )
    planned_weight: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    planned_start: Mapped[date | None] = mapped_column(Date)
    planned_finish: Mapped[date | None] = mapped_column(Date)
    actual_start: Mapped[date | None] = mapped_column(Date)
    actual_finish: Mapped[date | None] = mapped_column(Date)
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

    activity_instance: Mapped[ActivityInstance] = relationship()
    workflow_template: Mapped[WorkflowStepTemplate | None] = relationship(
        back_populates="workflow_steps",
    )
