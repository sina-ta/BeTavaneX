"""Read-only runtime aggregation and operational query composition."""

from __future__ import annotations

from collections import Counter
from datetime import date
from decimal import Decimal
from typing import Generic, TypedDict, TypeVar
from uuid import UUID

from backend.phase1.models.activity_instance import ActivityInstance
from backend.phase1.models.approval import Approval
from backend.phase1.models.blocker import Blocker
from backend.phase1.models.boq_mapping import BOQMapping
from backend.phase1.models.daily_report import DailyReport
from backend.phase1.models.inspection import Inspection
from backend.phase1.models.project import Project
from backend.phase1.models.work_order import WorkOrder
from backend.phase1.models.workflow_step import WorkflowStep
from backend.phase1.repositories.activity_instance_repository import (
    ActivityInstanceRepository,
    ActivityInstanceSortField,
    SortDirection as ActivitySortDirection,
)
from backend.phase1.repositories.approval_repository import ApprovalRepository
from backend.phase1.repositories.blocker_repository import BlockerRepository
from backend.phase1.repositories.boq_mapping_repository import BOQMappingRepository
from backend.phase1.repositories.daily_report_repository import (
    DailyReportRepository,
    DailyReportSortField,
    SortDirection as ReportSortDirection,
)
from backend.phase1.repositories.inspection_repository import InspectionRepository
from backend.phase1.repositories.project_repository import (
    ProjectRepository,
    ProjectSortField,
    SortDirection as ProjectSortDirection,
)
from backend.phase1.repositories.work_order_repository import (
    SortDirection as WorkOrderSortDirection,
    WorkOrderRepository,
    WorkOrderSortField,
)
from backend.phase1.repositories.workflow_step_repository import (
    WorkflowStepRepository,
    WorkflowStepSortField,
    SortDirection as StepSortDirection,
)
from backend.phase1.services.progress_service import ProgressService

ModelT = TypeVar("ModelT")


class PaginatedResult(TypedDict, Generic[ModelT]):
    items: list[ModelT]
    total: int


class ActivityInstanceProgressSummary(TypedDict):
    activity_instance_progress: Decimal
    workflow_step_progress: dict[str, Decimal]


class ActivityInstanceRuntimeView(TypedDict):
    activity_instance: ActivityInstance | None
    workflow_steps: list[WorkflowStep]
    progress_summary: ActivityInstanceProgressSummary


class WorkflowStepRuntimeView(TypedDict):
    workflow_step: WorkflowStep | None
    work_orders: list[WorkOrder]
    current_progress: Decimal
    inspections: list[Inspection]
    approvals: list[Approval]
    blockers: list[Blocker]
    boq_mappings: list[BOQMapping]


class WorkOrderRuntimeView(TypedDict):
    work_order: WorkOrder | None
    workflow_steps: list[WorkflowStep]
    daily_reports: list[DailyReport]


class ProjectRuntimeSummary(TypedDict):
    project_id: UUID
    project_progress: Decimal
    activity_instance_count: int
    workflow_step_count: int
    work_order_count: int


class ActivityInstanceProgressItem(TypedDict):
    activity_instance_id: UUID
    code: str
    name: str
    status: str
    progress_percent: Decimal


class WorkOrderStatusCount(TypedDict):
    status: str
    count: int


class ProjectDashboardSummary(TypedDict):
    project_id: UUID
    project_progress: Decimal
    activity_instance_count: int
    workflow_step_count: int
    work_order_count: int
    activity_instances: list[ActivityInstanceProgressItem]
    work_orders_by_status: list[WorkOrderStatusCount]


class WorkflowStepOperationalRow(TypedDict):
    workflow_step: WorkflowStep
    approvals: list[Approval]
    blockers: list[Blocker]


class ProjectWorkflowStepBatchRow(TypedDict):
    activity_instance_id: UUID
    activity_code: str
    activity_name: str
    workflow_step: WorkflowStep
    approvals: list[Approval]
    blockers: list[Blocker]


class RuntimeQueryService:
    """Read-only runtime views; no persistence or workflow side effects."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        activity_instance_repository: ActivityInstanceRepository,
        workflow_step_repository: WorkflowStepRepository,
        work_order_repository: WorkOrderRepository,
        daily_report_repository: DailyReportRepository,
        inspection_repository: InspectionRepository,
        approval_repository: ApprovalRepository,
        blocker_repository: BlockerRepository,
        boq_mapping_repository: BOQMappingRepository,
        progress_service: ProgressService,
    ) -> None:
        self._project_repository = project_repository
        self._activity_instance_repository = activity_instance_repository
        self._workflow_step_repository = workflow_step_repository
        self._work_order_repository = work_order_repository
        self._daily_report_repository = daily_report_repository
        self._inspection_repository = inspection_repository
        self._approval_repository = approval_repository
        self._blocker_repository = blocker_repository
        self._boq_mapping_repository = boq_mapping_repository
        self._progress_service = progress_service

    def get_activity_instance_runtime_view(
        self,
        activity_instance_id: UUID,
    ) -> ActivityInstanceRuntimeView:
        activity_instance = self._activity_instance_repository.get_by_id(
            activity_instance_id,
        )
        workflow_steps = self._workflow_step_repository.list(
            activity_instance_id=activity_instance_id,
        )

        step_progress: dict[str, Decimal] = {}
        for workflow_step in workflow_steps:
            step_progress[str(workflow_step.id)] = (
                self._progress_service.calculate_workflow_step_progress(
                    workflow_step.id,
                )
            )

        progress_summary: ActivityInstanceProgressSummary = {
            "activity_instance_progress": (
                self._progress_service.calculate_activity_instance_progress(
                    activity_instance_id,
                )
                if activity_instance is not None
                else Decimal("0")
            ),
            "workflow_step_progress": step_progress,
        }

        return {
            "activity_instance": activity_instance,
            "workflow_steps": workflow_steps,
            "progress_summary": progress_summary,
        }

    def get_workflow_step_runtime_view(
        self,
        workflow_step_id: UUID,
    ) -> WorkflowStepRuntimeView:
        workflow_step = self._workflow_step_repository.get_by_id(workflow_step_id)
        work_orders = self._work_orders_for_workflow_step(workflow_step_id, workflow_step)

        return {
            "workflow_step": workflow_step,
            "work_orders": work_orders,
            "current_progress": self._progress_service.calculate_workflow_step_progress(
                workflow_step_id,
            ),
            "inspections": self._inspection_repository.list(
                workflow_step_id=workflow_step_id,
            ),
            "approvals": self._approval_repository.list(
                workflow_step_id=workflow_step_id,
            ),
            "blockers": self._blocker_repository.list(
                workflow_step_id=workflow_step_id,
            ),
            "boq_mappings": self._boq_mapping_repository.list(
                workflow_step_id=workflow_step_id,
            ),
        }

    def get_work_order_project_id(self, work_order_id: UUID) -> UUID | None:
        work_order = self._work_order_repository.get_by_id(work_order_id)
        return work_order.project_id if work_order is not None else None

    def get_activity_instance_project_id(
        self,
        activity_instance_id: UUID,
    ) -> UUID | None:
        activity = self._activity_instance_repository.get_by_id(activity_instance_id)
        return activity.project_id if activity is not None else None

    def get_workflow_step_project_id(self, workflow_step_id: UUID) -> UUID | None:
        workflow_step = self._workflow_step_repository.get_by_id(workflow_step_id)
        if workflow_step is None:
            return None
        return self.get_activity_instance_project_id(workflow_step.activity_instance_id)

    def get_work_order_runtime_view(self, work_order_id: UUID) -> WorkOrderRuntimeView:
        work_order = self._work_order_repository.get_by_id(work_order_id)
        workflow_steps: list[WorkflowStep] = []
        if work_order is not None:
            for link in work_order.work_order_workflow_steps:
                workflow_step = self._workflow_step_repository.get_by_id(
                    link.workflow_step_id,
                )
                if workflow_step is not None:
                    workflow_steps.append(workflow_step)

        daily_reports = self._daily_report_repository.list(work_order_id=work_order_id)

        return {
            "work_order": work_order,
            "workflow_steps": workflow_steps,
            "daily_reports": daily_reports,
        }

    def get_project_runtime_summary(self, project_id: UUID) -> ProjectRuntimeSummary:
        activity_instances = self._activity_instance_repository.list_filtered(
            project_id=project_id,
            limit=10_000,
        )
        workflow_step_count = self._workflow_step_repository.count_by_project_id(
            project_id,
        )

        return {
            "project_id": project_id,
            "project_progress": self._progress_service.calculate_project_progress(
                project_id,
            ),
            "activity_instance_count": len(activity_instances),
            "workflow_step_count": workflow_step_count,
            "work_order_count": len(
                self._work_order_repository.list(project_id=project_id),
            ),
        }

    def get_project_dashboard_summary(self, project_id: UUID) -> ProjectDashboardSummary:
        summary = self.get_project_runtime_summary(project_id)
        activity_instances = self._activity_instance_repository.list_filtered(
            project_id=project_id,
            limit=10_000,
        )
        progress_items: list[ActivityInstanceProgressItem] = [
            {
                "activity_instance_id": instance.id,
                "code": instance.code,
                "name": instance.name,
                "status": instance.status,
                "progress_percent": self._progress_service.calculate_activity_instance_progress(
                    instance.id,
                ),
            }
            for instance in activity_instances
        ]
        work_orders = self._work_order_repository.list(project_id=project_id)
        status_counts = Counter(order.status for order in work_orders)

        return {
            **summary,
            "activity_instances": progress_items,
            "work_orders_by_status": [
                {"status": status, "count": count}
                for status, count in sorted(status_counts.items())
            ],
        }

    def list_projects(
        self,
        *,
        accessible_project_ids: set[UUID] | None = None,
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
        total = self._project_repository.count_filtered(
            project_ids=accessible_project_ids,
            name=name,
            status=status,
            planned_start_from=planned_start_from,
            planned_start_to=planned_start_to,
            planned_finish_from=planned_finish_from,
            planned_finish_to=planned_finish_to,
        )
        items = self._project_repository.list_filtered(
            project_ids=accessible_project_ids,
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
        return {"items": items, "total": total}

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
        total = self._activity_instance_repository.count_filtered(
            project_id=project_id,
            wbs_item_id=wbs_item_id,
            location_id=location_id,
            status=status,
        )
        items = self._activity_instance_repository.list_filtered(
            project_id=project_id,
            wbs_item_id=wbs_item_id,
            location_id=location_id,
            status=status,
            sort_by=sort_by,
            sort_dir=sort_dir,
            offset=offset,
            limit=limit,
        )
        return {"items": items, "total": total}

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
        total = self._workflow_step_repository.count_filtered(
            activity_instance_id=activity_instance_id,
            status=status,
            ready=ready,
        )
        steps = self._workflow_step_repository.list(
            activity_instance_id=activity_instance_id,
            status=status,
            ready=ready,
            sort_by=sort_by,
            sort_dir=sort_dir,
            offset=offset,
            limit=limit,
        )
        items: list[WorkflowStepOperationalRow] = []
        for step in steps:
            items.append(
                {
                    "workflow_step": step,
                    "approvals": self._approval_repository.list(
                        workflow_step_id=step.id,
                    ),
                    "blockers": self._blocker_repository.list(
                        workflow_step_id=step.id,
                    ),
                },
            )
        return {"items": items, "total": total}

    def list_project_workflow_steps_batch(
        self,
        project_id: UUID,
        *,
        status: str | None = None,
        offset: int = 0,
        limit: int = 500,
    ) -> PaginatedResult[ProjectWorkflowStepBatchRow]:
        """Single round-trip workflow step list for a project (batch dashboard support)."""
        total = self._workflow_step_repository.count_by_project_id(
            project_id,
            status=status,
        )
        steps = self._workflow_step_repository.list_by_project_id(
            project_id,
            status=status,
            offset=offset,
            limit=limit,
        )
        if not steps:
            return {"items": [], "total": total}

        step_ids = [step.id for step in steps]
        approvals = self._approval_repository.list_for_workflow_step_ids(step_ids)
        blockers = self._blocker_repository.list_for_workflow_step_ids(step_ids)

        approvals_by_step: dict[UUID, list[Approval]] = {}
        for approval in approvals:
            approvals_by_step.setdefault(approval.workflow_step_id, []).append(
                approval,
            )

        blockers_by_step: dict[UUID, list[Blocker]] = {}
        for blocker in blockers:
            blockers_by_step.setdefault(blocker.workflow_step_id, []).append(blocker)

        activity_instances = self._activity_instance_repository.list_filtered(
            project_id=project_id,
            limit=10_000,
        )
        activity_by_id = {instance.id: instance for instance in activity_instances}

        items: list[ProjectWorkflowStepBatchRow] = []
        for step in steps:
            activity = activity_by_id.get(step.activity_instance_id)
            items.append(
                {
                    "activity_instance_id": step.activity_instance_id,
                    "activity_code": activity.code if activity is not None else "",
                    "activity_name": activity.name if activity is not None else "",
                    "workflow_step": step,
                    "approvals": approvals_by_step.get(step.id, []),
                    "blockers": blockers_by_step.get(step.id, []),
                },
            )

        return {"items": items, "total": total}

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
        total = self._work_order_repository.count_filtered(
            project_id=project_id,
            status=status,
            workflow_step_id=workflow_step_id,
            planned_date_from=planned_date_from,
            planned_date_to=planned_date_to,
        )
        items = self._work_order_repository.list_filtered(
            project_id=project_id,
            status=status,
            workflow_step_id=workflow_step_id,
            planned_date_from=planned_date_from,
            planned_date_to=planned_date_to,
            sort_by=sort_by,
            sort_dir=sort_dir,
            offset=offset,
            limit=limit,
        )
        return {"items": items, "total": total}

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
        total = self._daily_report_repository.count_filtered(
            work_order_id=work_order_id,
            status=status,
            report_date_from=report_date_from,
            report_date_to=report_date_to,
        )
        items = self._daily_report_repository.list(
            work_order_id=work_order_id,
            status=status,
            report_date_from=report_date_from,
            report_date_to=report_date_to,
            sort_by=sort_by,
            sort_dir=sort_dir,
            offset=offset,
            limit=limit,
        )
        return {"items": items, "total": total}

    def _work_orders_for_workflow_step(
        self,
        workflow_step_id: UUID,
        workflow_step: WorkflowStep | None,
    ) -> list[WorkOrder]:
        if workflow_step is None:
            return []

        activity_instance = self._activity_instance_repository.get_by_id(
            workflow_step.activity_instance_id,
        )
        if activity_instance is None:
            return []

        related: list[WorkOrder] = []
        for work_order in self._work_order_repository.list(
            project_id=activity_instance.project_id,
        ):
            if any(
                link.workflow_step_id == workflow_step_id
                for link in work_order.work_order_workflow_steps
            ):
                related.append(work_order)
        return related
