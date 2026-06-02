"""BOQItem ORM model (Financial / Planning Layer)."""

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
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base

if TYPE_CHECKING:
    from backend.phase1.models.project import Project


class BOQItem(Base):
    __tablename__ = "boq_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="boq_items_quantity_positive_check"),
        CheckConstraint("rate >= 0", name="boq_items_rate_non_negative_check"),
        CheckConstraint(
            "status IN ('DRAFT', 'APPROVED', 'ACTIVE', 'CLOSED')",
            name="boq_items_status_check",
        ),
        Index("idx_boq_items_project_id", "project_id"),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "projects.id",
            name="boq_items_project_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    item_number: Mapped[str] = mapped_column(String(100), nullable=False)
    item_code: Mapped[str | None] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    rate: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    planned_cost: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        server_default="IRR",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default="ACTIVE",
    )
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

    project: Mapped[Project] = relationship(back_populates="boq_items")
