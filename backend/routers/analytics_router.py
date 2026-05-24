from fastapi import APIRouter

from backend.services.analytics_service import (
    get_project_kpi_trends,
    get_task_kpi_trends,
)

router = APIRouter()


@router.get("/analytics/kpi-trends")
def get_kpi_trends():
    return get_project_kpi_trends()


@router.get("/analytics/kpi-trends/{task_id}")
def get_task_trends(task_id: int):
    return get_task_kpi_trends(task_id)
