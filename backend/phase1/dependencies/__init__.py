"""Phase 1 FastAPI dependency providers (composition root for routers)."""

from backend.phase1.dependencies.application import get_runtime_use_cases
from backend.phase1.dependencies.repositories import (
    get_activity_instance_repository,
    get_approval_repository,
    get_blocker_repository,
    get_boq_item_repository,
    get_boq_mapping_repository,
    get_daily_report_repository,
    get_inspection_repository,
    get_project_repository,
    get_punch_item_repository,
    get_work_order_repository,
    get_work_order_workflow_step_repository,
    get_workflow_step_repository,
)
from backend.phase1.dependencies.services import (
    get_progress_service,
    get_runtime_query_service,
    get_workflow_execution_service,
    get_workflow_governance_service,
)

__all__ = [
    "get_activity_instance_repository",
    "get_approval_repository",
    "get_blocker_repository",
    "get_boq_item_repository",
    "get_boq_mapping_repository",
    "get_daily_report_repository",
    "get_inspection_repository",
    "get_progress_service",
    "get_project_repository",
    "get_punch_item_repository",
    "get_runtime_query_service",
    "get_runtime_use_cases",
    "get_work_order_repository",
    "get_work_order_workflow_step_repository",
    "get_workflow_execution_service",
    "get_workflow_governance_service",
    "get_workflow_step_repository",
]
