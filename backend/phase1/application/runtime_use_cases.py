"""Runtime use cases orchestrating Phase 1 services for future APIs."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from backend.phase1.models.approval import Approval
from backend.phase1.models.daily_report import DailyReport
from backend.phase1.models.work_order_workflow_step import WorkOrderWorkflowStep
from backend.phase1.services.progress_service import ProgressService
from backend.phase1.services.runtime_query_service import (
    ActivityInstanceRuntimeView,
    ProjectRuntimeSummary,
    RuntimeQueryService,
)
from backend.phase1.services.workflow_execution_service import (
    WorkflowExecutionService,
)
from backend.phase1.services.workflow_governance_service import (
    WorkflowGovernanceService,
)


class RuntimeUseCases:
    """Coordinates runtime services; no ORM, repository, or formula logic."""

    def __init__(
        self,
        progress_service: ProgressService,
        runtime_query_service: RuntimeQueryService,
        workflow_execution_service: WorkflowExecutionService,
        workflow_governance_service: WorkflowGovernanceService,
    ) -> None:
        self._progress_service = progress_service
        self._runtime_query_service = runtime_query_service
        self._workflow_execution_service = workflow_execution_service
        self._workflow_governance_service = workflow_governance_service

    def get_project_dashboard(self, project_id: UUID) -> ProjectRuntimeSummary:
        return self._runtime_query_service.get_project_runtime_summary(project_id)

    def get_activity_instance_dashboard(
        self,
        activity_instance_id: UUID,
    ) -> ActivityInstanceRuntimeView:
        return self._runtime_query_service.get_activity_instance_runtime_view(
            activity_instance_id,
        )

    def assign_work_order(
        self,
        work_order_id: UUID,
        workflow_step_id: UUID,
        execution_weight: Decimal,
    ) -> WorkOrderWorkflowStep:
        return self._workflow_execution_service.assign_work_order_to_workflow_step(
            work_order_id,
            workflow_step_id,
            execution_weight,
        )

    def submit_daily_report(
        self,
        work_order_id: UUID,
        report_date: date,
        *,
        status: str = "DRAFT",
        summary: str | None = None,
        execution_notes: str | None = None,
        issue_notes: str | None = None,
        delay_notes: str | None = None,
        weather_notes: str | None = None,
        evidence_metadata: dict[str, Any] | list[Any] | None = None,
        submitted_by: UUID | None = None,
        submitted_at: datetime | None = None,
        reported_manpower: int | None = None,
        reported_equipment: int | None = None,
        reported_material_entries: int | None = None,
    ) -> DailyReport:
        return self._workflow_execution_service.create_daily_report(
            work_order_id,
            report_date,
            status=status,
            summary=summary,
            execution_notes=execution_notes,
            issue_notes=issue_notes,
            delay_notes=delay_notes,
            weather_notes=weather_notes,
            evidence_metadata=evidence_metadata,
            submitted_by=submitted_by,
            submitted_at=submitted_at,
            reported_manpower=reported_manpower,
            reported_equipment=reported_equipment,
            reported_material_entries=reported_material_entries,
        )

    def approve_workflow_step(
        self,
        workflow_step_id: UUID,
        *,
        approval_type: str = "FINAL",
        approved_by: UUID | None = None,
        approval_date: date | None = None,
        approval_notes: str | None = None,
    ) -> Approval:
        return self._workflow_governance_service.approve_workflow_step(
            workflow_step_id,
            approval_type=approval_type,
            approved_by=approved_by,
            approval_date=approval_date,
            approval_notes=approval_notes,
        )
