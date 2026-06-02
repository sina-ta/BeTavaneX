"""BOQMapping ORM model (Financial Integration Layer)."""

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
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base

if TYPE_CHECKING:
    from backend.phase1.models.boq_item import BOQItem
    from backend.phase1.models.workflow_step import WorkflowStep


class BOQMapping(Base):
    __tablename__ = "boq_mappings"
    __table_args__ = (
        UniqueConstraint(
            "workflow_step_id",
            "boq_item_id",
            name="boq_mappings_workflow_step_boq_item_key",
        ),
        CheckConstraint(
            "allocated_quantity > 0",
            name="boq_mappings_allocated_quantity_positive_check",
        ),
        CheckConstraint(
            "allocated_cost >= 0",
            name="boq_mappings_allocated_cost_non_negative_check",
        ),
        CheckConstraint(
            "allocation_percentage IS NULL OR "
            "(allocation_percentage >= 0 AND allocation_percentage <= 100)",
            name="boq_mappings_allocation_percentage_range_check",
        ),
        Index("idx_boq_mappings_workflow_step_id", "workflow_step_id"),
        Index("idx_boq_mappings_boq_item_id", "boq_item_id"),
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
            name="boq_mappings_workflow_step_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    boq_item_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "boq_items.id",
            name="boq_mappings_boq_item_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    allocated_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    allocated_cost: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    allocation_percentage: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    notes: Mapped[str | None] = mapped_column(Text)
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
    boq_item: Mapped[BOQItem] = relationship()
