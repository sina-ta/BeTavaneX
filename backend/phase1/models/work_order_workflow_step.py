"""WorkOrderWorkflowStep junction ORM model (Execution Coordination Layer)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base

if TYPE_CHECKING:
    from backend.phase1.models.work_order import WorkOrder
    from backend.phase1.models.workflow_step import WorkflowStep


class WorkOrderWorkflowStep(Base):
    __tablename__ = "work_order_workflow_steps"
    __table_args__ = (
        UniqueConstraint(
            "work_order_id",
            "workflow_step_id",
            name="work_order_workflow_steps_work_order_step_key",
        ),
        CheckConstraint(
            "execution_weight > 0 AND execution_weight <= 100",
            name="work_order_workflow_steps_execution_weight_positive_check",
        ),
        Index(
            "idx_work_order_workflow_steps_work_order_id",
            "work_order_id",
        ),
        Index(
            "idx_work_order_workflow_steps_workflow_step_id",
            "workflow_step_id",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    work_order_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "work_orders.id",
            name="work_order_workflow_steps_work_order_id_fkey",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    workflow_step_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "workflow_steps.id",
            name="work_order_workflow_steps_workflow_step_id_fkey",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    execution_weight: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    work_order: Mapped[WorkOrder] = relationship(
        back_populates="work_order_workflow_steps",
    )
    workflow_step: Mapped[WorkflowStep] = relationship()
