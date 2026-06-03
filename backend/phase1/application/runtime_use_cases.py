"""Runtime use cases orchestrating Phase 1 services for future APIs."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from backend.phase1.auth.auth import User
from backend.phase1.auth.project_access import ProjectAccessService
from backend.phase1.models.activity_instance import ActivityInstance
from backend.phase1.models.approval import Approval
from backend.phase1.models.daily_report import DailyReport
from backend.phase1.models.project import Project
from backend.phase1.models.work_order import WorkOrder
from backend.phase1.models.work_order_workflow_step import WorkOrderWorkflowStep
from backend.phase1.repositories.work_order_repository import (
    SortDirection as WorkOrderSortDirection,
    WorkOrderSortField,
)
from backend.phase1.repositories.activity_instance_repository import (
    ActivityInstanceSortField,
    SortDirection as ActivitySortDirection,
)
from backend.phase1.repositories.daily_report_repository import (
    DailyReportSortField,
    SortDirection as ReportSortDirection,
)
from backend.phase1.repositories.project_repository import (
    ProjectSortField,
    SortDirection as ProjectSortDirection,
)
from backend.phase1.repositories.workflow_step_repository import (
    WorkflowStepSortField,
    SortDirection as StepSortDirection,
)
from backend.phase1.services.progress_service import ProgressService
from backend.phase1.services.runtime_query_service import (
    ActivityInstanceRuntimeView,
    PaginatedResult,
    ProjectDashboardSummary,
    ProjectRuntimeSummary,
    RuntimeQueryService,
    WorkflowStepOperationalRow,
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
        project_access_service: ProjectAccessService,
    ) -> None:
        self._progress_service = progress_service
        self._runtime_query_service = runtime_query_service
        self._workflow_execution_service = workflow_execution_service
        self._workflow_governance_service = workflow_governance_service
        self._project_access = project_access_service

    def get_project_dashboard(self, project_id: UUID) -> ProjectRuntimeSummary:
        return self._runtime_query_service.get_project_runtime_summary(project_id)

    def get_project_dashboard_summary(self, project_id: UUID) -> ProjectDashboardSummary:
        return self._runtime_query_service.get_project_dashboard_summary(project_id)

    def list_projects(
        self,
        current_user: User,
        *,
        name: str | None = None,
        status: str | None = None,
        planned_start_from: date | None = None,
        planned_start_to: date | None = None,
        planned_finish_from: date | None = None,
        planned_finish_to: date | None = None,
        sort_by: ProjectSortField = "created_at",
        sort_dir: ProjectSortDirection = "desc",
        offset: int = 0,
        limit: int = 50,
    ) -> PaginatedResult[Project]:
        return self._runtime_query_service.list_projects(
            accessible_project_ids=self._project_access.get_accessible_project_ids(
                current_user,
            ),
            name=name,
            status=status,
            planned_start_from=planned_start_from,
            planned_start_to=planned_start_to,
            planned_finish_from=planned_finish_from,
            planned_finish_to=planned_finish_to,
            sort_by=sort_by,
            sort_dir=sort_dir,
            offset=offset,
            limit=limit,
        )

    def list_activity_instances(
        self,
        project_id: UUID,
        *,
        wbs_item_id: UUID | None = None,
        location_id: UUID | None = None,
        status: str | None = None,
        sort_by: ActivityInstanceSortField = "created_at",
        sort_dir: ActivitySortDirection = "desc",
        offset: int = 0,
        limit: int = 50,
    ) -> PaginatedResult[ActivityInstance]:
        return self._runtime_query_service.list_activity_instances(
            project_id,
            wbs_item_id=wbs_item_id,
            location_id=location_id,
            status=status,
            sort_by=sort_by,
            sort_dir=sort_dir,
            offset=offset,
            limit=limit,
        )

    def list_project_workflow_steps_batch(
        self,
        project_id: UUID,
        *,
        status: str | None = None,
        offset: int = 0,
        limit: int = 500,
    ):
        return self._runtime_query_service.list_project_workflow_steps_batch(
            project_id,
            status=status,
            offset=offset,
            limit=limit,
        )

    def list_workflow_steps(
        self,
        activity_instance_id: UUID,
        *,
        status: str | None = None,
        ready: bool | None = None,
        sort_by: WorkflowStepSortField = "created_at",
        sort_dir: StepSortDirection = "desc",
        offset: int = 0,
        limit: int = 50,
    ) -> PaginatedResult[WorkflowStepOperationalRow]:
        return self._runtime_query_service.list_workflow_steps(
            activity_instance_id,
            status=status,
            ready=ready,
            sort_by=sort_by,
            sort_dir=sort_dir,
            offset=offset,
            limit=limit,
        )

    def list_work_orders(
        self,
        project_id: UUID,
        *,
        status: str | None = None,
        workflow_step_id: UUID | None = None,
        planned_date_from: date | None = None,
        planned_date_to: date | None = None,
        sort_by: WorkOrderSortField = "planned_date",
        sort_dir: WorkOrderSortDirection = "desc",
        offset: int = 0,
        limit: int = 50,
    ) -> PaginatedResult[WorkOrder]:
        return self._runtime_query_service.list_work_orders(
            project_id,
            status=status,
            workflow_step_id=workflow_step_id,
            planned_date_from=planned_date_from,
            planned_date_to=planned_date_to,
            sort_by=sort_by,
            sort_dir=sort_dir,
            offset=offset,
            limit=limit,
        )

    def list_daily_reports(
        self,
        work_order_id: UUID,
        *,
        status: str | None = None,
        report_date_from: date | None = None,
        report_date_to: date | None = None,
        sort_by: DailyReportSortField = "report_date",
        sort_dir: ReportSortDirection = "desc",
        offset: int = 0,
        limit: int = 50,
    ) -> PaginatedResult[DailyReport]:
        return self._runtime_query_service.list_daily_reports(
            work_order_id,
            status=status,
            report_date_from=report_date_from,
            report_date_to=report_date_to,
            sort_by=sort_by,
            sort_dir=sort_dir,
            offset=offset,
            limit=limit,
        )

    def get_activity_instance_dashboard(
        self,
        activity_instance_id: UUID,
    ) -> ActivityInstanceRuntimeView:
        return self._runtime_query_service.get_activity_instance_runtime_view(
            activity_instance_id,
        )

    def get_work_order_project_id(self, work_order_id: UUID) -> UUID | None:
        return self._runtime_query_service.get_work_order_project_id(work_order_id)

    def get_activity_instance_project_id(
        self,
        activity_instance_id: UUID,
    ) -> UUID | None:
        return self._runtime_query_service.get_activity_instance_project_id(
            activity_instance_id,
        )

    def get_workflow_step_project_id(self, workflow_step_id: UUID) -> UUID | None:
        return self._runtime_query_service.get_workflow_step_project_id(
            workflow_step_id,
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
        expected_work_order_updated_at: datetime | None = None,
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
            expected_work_order_updated_at=expected_work_order_updated_at,
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
        expected_workflow_step_updated_at: datetime | None = None,
    ) -> Approval:
        return self._workflow_governance_service.approve_workflow_step(
            workflow_step_id,
            approval_type=approval_type,
            approved_by=approved_by,
            approval_date=approval_date,
            approval_notes=approval_notes,
            expected_workflow_step_updated_at=expected_workflow_step_updated_at,
        )
