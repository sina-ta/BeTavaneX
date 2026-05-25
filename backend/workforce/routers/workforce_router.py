from fastapi import APIRouter, Query

from backend.workforce.services.workforce_service import (
    list_workers_service,
    get_worker_detail_service,
    get_worker_intelligence_service,
    get_workforce_analytics_service,
    list_crews_service,
    check_eligibility_service,
)

router = APIRouter(prefix="/workforce", tags=["workforce"])


@router.get("/workers")
def list_workers():
    return list_workers_service()


@router.get("/workers/analytics")
def workforce_analytics():
    return get_workforce_analytics_service()


@router.get("/workers/{worker_id}")
def get_worker(worker_id: int):
    return get_worker_detail_service(worker_id)


@router.get("/workers/{worker_id}/intelligence")
def get_worker_intelligence(worker_id: int):
    return get_worker_intelligence_service(worker_id)


@router.get("/workers/{worker_id}/eligibility")
def get_worker_eligibility(
    worker_id: int,
    task_id: int | None = Query(default=None),
):
    return check_eligibility_service(worker_id, task_id)


@router.get("/crews")
def list_crews():
    return list_crews_service()
