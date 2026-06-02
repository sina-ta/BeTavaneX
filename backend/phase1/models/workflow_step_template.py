"""WorkflowStepTemplate ORM model (Execution Knowledge Layer)."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Index,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base

if TYPE_CHECKING:
    from backend.phase1.models.workflow_step import WorkflowStep


class WorkflowStepTemplate(Base):
    __tablename__ = "workflow_step_templates"
    __table_args__ = (
        CheckConstraint(
            "status IN ('ACTIVE', 'ARCHIVED')",
            name="workflow_step_templates_status_check",
        ),
        Index("idx_workflow_step_templates_status", "status"),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    method_statement: Mapped[str | None] = mapped_column(Text)
    safety_requirements: Mapped[str | None] = mapped_column(Text)
    inspection_checklist: Mapped[str | None] = mapped_column(Text)
    required_resources: Mapped[dict[str, Any] | list[Any] | None] = mapped_column(JSONB)
    required_permits: Mapped[dict[str, Any] | list[Any] | None] = mapped_column(JSONB)
    required_documents: Mapped[dict[str, Any] | list[Any] | None] = mapped_column(JSONB)
    execution_guide: Mapped[str | None] = mapped_column(Text)
    standard_references: Mapped[str | None] = mapped_column(Text)
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

    workflow_steps: Mapped[list["WorkflowStep"]] = relationship(
        back_populates="workflow_template",
    )
