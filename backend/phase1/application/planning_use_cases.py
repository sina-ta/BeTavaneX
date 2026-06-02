"""Planning use cases: expose planning persistence through the application layer.

This layer is a thin persistence facade. It contains no business rules, no
workflow/progress/readiness calculation, and no planning intelligence — it only
constructs ORM entities and delegates to repositories.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from backend.phase1.models.activity_instance import ActivityInstance
from backend.phase1.models.location import Location
from backend.phase1.models.project import Project
from backend.phase1.models.wbs_item import WBSItem
from backend.phase1.models.work_order import WorkOrder
from backend.phase1.models.workflow_step import WorkflowStep
from backend.phase1.repositories.activity_instance_repository import (
    ActivityInstanceRepository,
)
from backend.phase1.repositories.location_repository import LocationRepository
from backend.phase1.repositories.project_repository import ProjectRepository
from backend.phase1.repositories.wbs_item_repository import WBSItemRepository
from backend.phase1.repositories.work_order_repository import WorkOrderRepository
from backend.phase1.repositories.workflow_step_repository import WorkflowStepRepository


class PlanningUseCases:
    """Persistence-only orchestration for planning entity creation."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        wbs_item_repository: WBSItemRepository,
        location_repository: LocationRepository,
        activity_instance_repository: ActivityInstanceRepository,
        workflow_step_repository: WorkflowStepRepository,
        work_order_repository: WorkOrderRepository,
    ) -> None:
        self._project_repository = project_repository
        self._wbs_item_repository = wbs_item_repository
        self._location_repository = location_repository
        self._activity_instance_repository = activity_instance_repository
        self._workflow_step_repository = workflow_step_repository
        self._work_order_repository = work_order_repository

    def create_project(
        self,
        code: str,
        name: str,
        *,
        description: str | None = None,
        status: str = "ACTIVE",
        planned_start: date | None = None,
        planned_finish: date | None = None,
    ) -> Project:
        project = Project(
            code=code,
            name=name,
            description=description,
            status=status,
            planned_start=planned_start,
            planned_finish=planned_finish,
        )
        return self._project_repository.create(project)

    def create_wbs_item(
        self,
        project_id: UUID,
        code: str,
        name: str,
        level: int,
        *,
        parent_id: UUID | None = None,
        description: str | None = None,
        status: str = "ACTIVE",
    ) -> WBSItem:
        wbs_item = WBSItem(
            project_id=project_id,
            parent_id=parent_id,
            code=code,
            name=name,
            description=description,
            level=level,
            status=status,
        )
        return self._wbs_item_repository.create(wbs_item)

    def create_location(
        self,
        project_id: UUID,
        code: str,
        name: str,
        level: int,
        *,
        parent_id: UUID | None = None,
        description: str | None = None,
        status: str = "ACTIVE",
    ) -> Location:
        location = Location(
            project_id=project_id,
            parent_id=parent_id,
            code=code,
            name=name,
            description=description,
            level=level,
            status=status,
        )
        return self._location_repository.create(location)

    def create_activity_instance(
        self,
        project_id: UUID,
        wbs_item_id: UUID,
        location_id: UUID,
        code: str,
        name: str,
        *,
        planned_start: date | None = None,
        planned_finish: date | None = None,
        planned_duration_days: int | None = None,
        status: str = "ACTIVE",
    ) -> ActivityInstance:
        activity_instance = ActivityInstance(
            project_id=project_id,
            wbs_item_id=wbs_item_id,
            location_id=location_id,
            code=code,
            name=name,
            planned_start=planned_start,
            planned_finish=planned_finish,
            planned_duration_days=planned_duration_days,
            status=status,
        )
        return self._activity_instance_repository.create(activity_instance)

    def create_workflow_step(
        self,
        activity_instance_id: UUID,
        code: str,
        name: str,
        status: str,
        *,
        workflow_template_id: UUID | None = None,
        ready: bool = False,
        progress_percent: Decimal = Decimal("0"),
        planned_weight: Decimal | None = None,
        planned_start: date | None = None,
        planned_finish: date | None = None,
        actual_start: date | None = None,
        actual_finish: date | None = None,
    ) -> WorkflowStep:
        workflow_step = WorkflowStep(
            activity_instance_id=activity_instance_id,
            workflow_template_id=workflow_template_id,
            code=code,
            name=name,
            status=status,
            ready=ready,
            progress_percent=progress_percent,
            planned_weight=planned_weight,
            planned_start=planned_start,
            planned_finish=planned_finish,
            actual_start=actual_start,
            actual_finish=actual_finish,
        )
        return self._workflow_step_repository.create(workflow_step)

    def create_work_order(
        self,
        project_id: UUID,
        work_order_number: str,
        title: str,
        planned_date: date,
        *,
        description: str | None = None,
        status: str = "CREATED",
        created_by: UUID | None = None,
    ) -> WorkOrder:
        work_order = WorkOrder(
            project_id=project_id,
            work_order_number=work_order_number,
            title=title,
            description=description,
            planned_date=planned_date,
            status=status,
            created_by=created_by,
        )
        return self._work_order_repository.create(work_order)
