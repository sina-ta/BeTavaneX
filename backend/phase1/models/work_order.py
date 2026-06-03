"""WorkOrder ORM model (Execution Coordination Layer)."""

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
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base

if TYPE_CHECKING:
    from backend.phase1.models.daily_report import DailyReport
    from backend.phase1.models.project import Project
    from backend.phase1.models.work_order_workflow_step import WorkOrderWorkflowStep


class WorkOrder(Base):
    __tablename__ = "work_orders"
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "work_order_number",
            name="work_orders_project_id_work_order_number_key",
        ),
        CheckConstraint(
            "status IN ('CREATED', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')",
            name="work_orders_status_check",
        ),
        Index("idx_work_orders_project_id", "project_id"),
        Index("idx_work_orders_planned_date", "planned_date"),
        Index(
            "idx_work_orders_project_planned_date",
            "project_id",
            "planned_date",
        ),
        Index("idx_work_orders_status", "status"),
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
            name="work_orders_project_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    work_order_number: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    planned_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default="CREATED",
    )
    created_by: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
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

    project: Mapped[Project] = relationship()
    work_order_workflow_steps: Mapped[list["WorkOrderWorkflowStep"]] = relationship(
        back_populates="work_order",
        cascade="all, delete-orphan",
    )
    daily_reports: Mapped[list["DailyReport"]] = relationship(
        back_populates="work_order",
    )
