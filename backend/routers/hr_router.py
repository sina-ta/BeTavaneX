from fastapi import APIRouter

from backend.services.hr_service import (
    get_workers_service
)

router = APIRouter()


@router.get("/workers")
def get_workers():

    return get_workers_service()