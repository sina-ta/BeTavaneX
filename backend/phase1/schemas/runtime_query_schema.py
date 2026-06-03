"""Operational query / dashboard-summary response schemas."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from backend.phase1.schemas.approval_schema import ApprovalRead
from backend.phase1.schemas.blocker_schema import BlockerRead
from backend.phase1.schemas.workflow_step_schema import WorkflowStepRead


class WorkflowStepOperationalRead(BaseModel):
    """Workflow step read model plus operational context for list views."""

    workflow_step: WorkflowStepRead
    approvals: list[ApprovalRead] = Field(default_factory=list)
    blockers: list[BlockerRead] = Field(default_factory=list)


class ProjectWorkflowStepBatchItemRead(BaseModel):
    """Workflow step with parent activity context for project-scoped batch queries."""

    activity_instance_id: UUID
    activity_code: str
    activity_name: str
    workflow_step: WorkflowStepRead
    approvals: list[ApprovalRead] = Field(default_factory=list)
    blockers: list[BlockerRead] = Field(default_factory=list)


class ActivityInstanceProgressItem(BaseModel):
    activity_instance_id: UUID
    code: str
    name: str
    status: str
    progress_percent: Decimal


class WorkOrderStatusCount(BaseModel):
    status: str
    count: int = Field(ge=0)


class ProjectDashboardSummaryRead(BaseModel):
    project_id: UUID
    project_progress: Decimal
    activity_instance_count: int = Field(ge=0)
    workflow_step_count: int = Field(ge=0)
    work_order_count: int = Field(ge=0)
    activity_instances: list[ActivityInstanceProgressItem] = Field(default_factory=list)
    work_orders_by_status: list[WorkOrderStatusCount] = Field(default_factory=list)
