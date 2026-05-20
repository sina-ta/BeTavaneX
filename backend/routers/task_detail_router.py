from fastapi import APIRouter

from backend.services.task_detail_service import (
    get_task_detail_service
)

router = APIRouter()


@router.get("/task/{task_id}")

def get_task_detail(task_id: int):

    return get_task_detail_service(task_id)