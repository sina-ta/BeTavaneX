"""Planning router: thin FastAPI surface over PlanningUseCases.

Endpoints validate input via Pydantic schemas, delegate to the application
layer, and return Read schemas. No business logic, no repository access.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from backend.phase1.application.planning_use_cases import PlanningUseCases
from backend.phase1.dependencies.application import get_planning_use_cases
from backend.phase1.schemas.activity_instance_schema import (
    ActivityInstanceCreate,
    ActivityInstanceRead,
)
from backend.phase1.schemas.location_schema import LocationCreate, LocationRead
from backend.phase1.schemas.project_schema import ProjectCreate, ProjectRead
from backend.phase1.schemas.wbs_item_schema import WBSItemCreate, WBSItemRead
from backend.phase1.schemas.work_order_schema import WorkOrderCreate, WorkOrderRead
from backend.phase1.schemas.workflow_step_schema import (
    WorkflowStepCreate,
    WorkflowStepRead,
)

router = APIRouter(prefix="/planning", tags=["planning"])


@router.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    planning: PlanningUseCases = Depends(get_planning_use_cases),
) -> ProjectRead:
    return planning.create_project(
        code=payload.code,
        name=payload.name,
        description=payload.description,
        status=payload.status,
        planned_start=payload.planned_start,
        planned_finish=payload.planned_finish,
    )


@router.post("/wbs-items", response_model=WBSItemRead, status_code=status.HTTP_201_CREATED)
def create_wbs_item(
    payload: WBSItemCreate,
    planning: PlanningUseCases = Depends(get_planning_use_cases),
) -> WBSItemRead:
    return planning.create_wbs_item(
        payload.project_id,
        code=payload.code,
        name=payload.name,
        level=payload.level,
        parent_id=payload.parent_id,
        description=payload.description,
        status=payload.status,
    )


@router.post("/locations", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
def create_location(
    payload: LocationCreate,
    planning: PlanningUseCases = Depends(get_planning_use_cases),
) -> LocationRead:
    return planning.create_location(
        payload.project_id,
        code=payload.code,
        name=payload.name,
        level=payload.level,
        parent_id=payload.parent_id,
        description=payload.description,
        status=payload.status,
    )


@router.post(
    "/activity-instances",
    response_model=ActivityInstanceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_activity_instance(
    payload: ActivityInstanceCreate,
    planning: PlanningUseCases = Depends(get_planning_use_cases),
) -> ActivityInstanceRead:
    return planning.create_activity_instance(
        payload.project_id,
        payload.wbs_item_id,
        payload.location_id,
        code=payload.code,
        name=payload.name,
        planned_start=payload.planned_start,
        planned_finish=payload.planned_finish,
        planned_duration_days=payload.planned_duration_days,
        status=payload.status,
    )


@router.post(
    "/workflow-steps",
    response_model=WorkflowStepRead,
    status_code=status.HTTP_201_CREATED,
)
def create_workflow_step(
    payload: WorkflowStepCreate,
    planning: PlanningUseCases = Depends(get_planning_use_cases),
) -> WorkflowStepRead:
    return planning.create_workflow_step(
        payload.activity_instance_id,
        code=payload.code,
        name=payload.name,
        status=payload.status,
        workflow_template_id=payload.workflow_template_id,
        ready=payload.ready,
        progress_percent=payload.progress_percent,
        planned_weight=payload.planned_weight,
        planned_start=payload.planned_start,
        planned_finish=payload.planned_finish,
        actual_start=payload.actual_start,
        actual_finish=payload.actual_finish,
    )


@router.post("/work-orders", response_model=WorkOrderRead, status_code=status.HTTP_201_CREATED)
def create_work_order(
    payload: WorkOrderCreate,
    planning: PlanningUseCases = Depends(get_planning_use_cases),
) -> WorkOrderRead:
    return planning.create_work_order(
        payload.project_id,
        work_order_number=payload.work_order_number,
        title=payload.title,
        planned_date=payload.planned_date,
        description=payload.description,
        status=payload.status,
        created_by=payload.created_by,
    )
