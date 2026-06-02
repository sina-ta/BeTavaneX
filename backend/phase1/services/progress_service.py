"""Progress aggregation for WorkflowStep, ActivityInstance, and Project."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from backend.phase1.repositories.activity_instance_repository import (
    ActivityInstanceRepository,
)
from backend.phase1.repositories.project_repository import ProjectRepository
from backend.phase1.repositories.work_order_repository import WorkOrderRepository
from backend.phase1.repositories.workflow_step_repository import WorkflowStepRepository

_COMPLETED_WORK_ORDER_STATUS = "COMPLETED"
_PERCENT_SCALE = Decimal("0.01")
_HUNDRED = Decimal("100")


class ProgressService:
    """Commitment-based progress from WorkOrder execution weights (Phase 1)."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        activity_instance_repository: ActivityInstanceRepository,
        workflow_step_repository: WorkflowStepRepository,
        work_order_repository: WorkOrderRepository,
    ) -> None:
        self._project_repository = project_repository
        self._activity_instance_repository = activity_instance_repository
        self._workflow_step_repository = workflow_step_repository
        self._work_order_repository = work_order_repository

    def calculate_workflow_step_progress(self, workflow_step_id: UUID) -> Decimal:
        """
        Sum(completed WorkOrder execution_weight) / Sum(all execution_weight) × 100
        for links on this WorkflowStep.
        """
        workflow_step = self._workflow_step_repository.get_by_id(workflow_step_id)
        if workflow_step is None:
            return Decimal("0")

        activity_instance = self._activity_instance_repository.get_by_id(
            workflow_step.activity_instance_id,
        )
        if activity_instance is None:
            return Decimal("0")

        total_weight = Decimal("0")
        completed_weight = Decimal("0")

        work_orders = self._work_order_repository.list(
            project_id=activity_instance.project_id,
        )
        for work_order in work_orders:
            for link in work_order.work_order_workflow_steps:
                if link.workflow_step_id != workflow_step_id:
                    continue
                weight = Decimal(link.execution_weight)
                total_weight += weight
                if work_order.status == _COMPLETED_WORK_ORDER_STATUS:
                    completed_weight += weight

        if total_weight == 0:
            return Decimal("0")

        return _quantize_percent(completed_weight / total_weight * _HUNDRED)

    def persist_workflow_step_progress(self, workflow_step_id: UUID) -> Decimal:
        """Calculate WorkflowStep progress and store on progress_percent."""
        workflow_step = self._workflow_step_repository.get_by_id(workflow_step_id)
        if workflow_step is None:
            msg = f"WorkflowStep not found: {workflow_step_id}"
            raise ValueError(msg)

        progress = self.calculate_workflow_step_progress(workflow_step_id)
        workflow_step.progress_percent = progress
        self._workflow_step_repository.update(workflow_step)
        return progress

    def calculate_activity_instance_progress(
        self,
        activity_instance_id: UUID,
    ) -> Decimal:
        """Average of child WorkflowStep progress (unweighted, Phase 1)."""
        workflow_steps = self._workflow_step_repository.list(
            activity_instance_id=activity_instance_id,
        )
        if not workflow_steps:
            return Decimal("0")

        progress_total = Decimal("0")
        for workflow_step in workflow_steps:
            progress_total += self.calculate_workflow_step_progress(workflow_step.id)

        return _quantize_percent(progress_total / Decimal(len(workflow_steps)))

    def calculate_project_progress(self, project_id: UUID) -> Decimal:
        """Average of ActivityInstance progress (unweighted, Phase 1)."""
        if self._project_repository.get_by_id(project_id) is None:
            return Decimal("0")

        activity_instances = [
            instance
            for instance in self._activity_instance_repository.list()
            if instance.project_id == project_id
        ]
        if not activity_instances:
            return Decimal("0")

        progress_total = Decimal("0")
        for activity_instance in activity_instances:
            progress_total += self.calculate_activity_instance_progress(
                activity_instance.id,
            )

        return _quantize_percent(progress_total / Decimal(len(activity_instances)))


def _quantize_percent(value: Decimal) -> Decimal:
    return value.quantize(_PERCENT_SCALE, rounding=ROUND_HALF_UP)
