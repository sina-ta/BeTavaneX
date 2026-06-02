"""Read-only runtime aggregation for future API composition."""

from __future__ import annotations

from decimal import Decimal
from typing import TypedDict
from uuid import UUID

from backend.phase1.models.activity_instance import ActivityInstance
from backend.phase1.models.approval import Approval
from backend.phase1.models.blocker import Blocker
from backend.phase1.models.boq_mapping import BOQMapping
from backend.phase1.models.daily_report import DailyReport
from backend.phase1.models.inspection import Inspection
from backend.phase1.models.work_order import WorkOrder
from backend.phase1.models.workflow_step import WorkflowStep
from backend.phase1.repositories.activity_instance_repository import (
    ActivityInstanceRepository,
)
from backend.phase1.repositories.approval_repository import ApprovalRepository
from backend.phase1.repositories.blocker_repository import BlockerRepository
from backend.phase1.repositories.boq_mapping_repository import BOQMappingRepository
from backend.phase1.repositories.daily_report_repository import DailyReportRepository
from backend.phase1.repositories.inspection_repository import InspectionRepository
from backend.phase1.repositories.work_order_repository import WorkOrderRepository
from backend.phase1.repositories.workflow_step_repository import WorkflowStepRepository
from backend.phase1.services.progress_service import ProgressService


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


class RuntimeQueryService:
    """Read-only runtime views; no persistence or workflow side effects."""

    def __init__(
        self,
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
        activity_instances = [
            instance
            for instance in self._activity_instance_repository.list()
            if instance.project_id == project_id
        ]
        workflow_step_count = sum(
            len(
                self._workflow_step_repository.list(
                    activity_instance_id=instance.id,
                ),
            )
            for instance in activity_instances
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
