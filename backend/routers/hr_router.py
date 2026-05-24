from fastapi import APIRouter

from backend.services.hr_service import (
    get_workers_service,
)

from backend.services.worker_intelligence_service import (
    get_worker_intelligence_service,
    get_workforce_analytics_service,
)

router = APIRouter()


@router.get("/workers")
def get_workers():
    return get_workers_service()


@router.get("/workers/analytics")
def get_workforce_analytics():
    return get_workforce_analytics_service()


@router.get("/workers/{worker_id}")
def get_worker(worker_id: int):
    return get_worker_intelligence_service(worker_id)


@router.get("/workers/{worker_id}/intelligence")
def get_worker_intelligence(worker_id: int):
    return get_worker_intelligence_service(worker_id)
