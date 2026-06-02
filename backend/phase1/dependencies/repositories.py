"""Repository dependency providers.

Each provider builds a repository from the request-scoped session yielded by
``get_db``. FastAPI caches ``get_db`` per request, so every repository in a
single request shares one Session (and therefore one transaction boundary).

Providers construct objects only; they never query, mutate, or compute.
"""

from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.phase1.repositories.activity_instance_repository import (
    ActivityInstanceRepository,
)
from backend.phase1.repositories.approval_repository import ApprovalRepository
from backend.phase1.repositories.blocker_repository import BlockerRepository
from backend.phase1.repositories.boq_item_repository import BOQItemRepository
from backend.phase1.repositories.boq_mapping_repository import BOQMappingRepository
from backend.phase1.repositories.daily_report_repository import DailyReportRepository
from backend.phase1.repositories.inspection_repository import InspectionRepository
from backend.phase1.repositories.location_repository import LocationRepository
from backend.phase1.repositories.project_repository import ProjectRepository
from backend.phase1.repositories.punch_item_repository import PunchItemRepository
from backend.phase1.repositories.wbs_item_repository import WBSItemRepository
from backend.phase1.repositories.work_order_repository import WorkOrderRepository
from backend.phase1.repositories.work_order_workflow_step_repository import (
    WorkOrderWorkflowStepRepository,
)
from backend.phase1.repositories.workflow_step_repository import WorkflowStepRepository


def get_project_repository(
    session: Session = Depends(get_db),
) -> ProjectRepository:
    return ProjectRepository(session)


def get_wbs_item_repository(
    session: Session = Depends(get_db),
) -> WBSItemRepository:
    return WBSItemRepository(session)


def get_location_repository(
    session: Session = Depends(get_db),
) -> LocationRepository:
    return LocationRepository(session)


def get_activity_instance_repository(
    session: Session = Depends(get_db),
) -> ActivityInstanceRepository:
    return ActivityInstanceRepository(session)


def get_workflow_step_repository(
    session: Session = Depends(get_db),
) -> WorkflowStepRepository:
    return WorkflowStepRepository(session)


def get_work_order_repository(
    session: Session = Depends(get_db),
) -> WorkOrderRepository:
    return WorkOrderRepository(session)


def get_daily_report_repository(
    session: Session = Depends(get_db),
) -> DailyReportRepository:
    return DailyReportRepository(session)


def get_boq_item_repository(
    session: Session = Depends(get_db),
) -> BOQItemRepository:
    return BOQItemRepository(session)


def get_inspection_repository(
    session: Session = Depends(get_db),
) -> InspectionRepository:
    return InspectionRepository(session)


def get_punch_item_repository(
    session: Session = Depends(get_db),
) -> PunchItemRepository:
    return PunchItemRepository(session)


def get_approval_repository(
    session: Session = Depends(get_db),
) -> ApprovalRepository:
    return ApprovalRepository(session)


def get_blocker_repository(
    session: Session = Depends(get_db),
) -> BlockerRepository:
    return BlockerRepository(session)


def get_boq_mapping_repository(
    session: Session = Depends(get_db),
) -> BOQMappingRepository:
    return BOQMappingRepository(session)


def get_work_order_workflow_step_repository(
    session: Session = Depends(get_db),
) -> WorkOrderWorkflowStepRepository:
    return WorkOrderWorkflowStepRepository(session)
