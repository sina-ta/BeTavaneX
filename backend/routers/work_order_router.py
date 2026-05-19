from fastapi import APIRouter

from backend.database import SessionLocal

from backend.models import DailyWorkOrder

from backend.schemas import WorkOrderCreate

from backend.services.work_order_service import (
    create_work_order_service
)

from backend.services.work_order_service import (
    create_work_order_service,
    get_work_orders_service
)

router = APIRouter()


@router.post("/daily-work-order")
def create_work_order(work_order: WorkOrderCreate):

    return create_work_order_service(work_order)


@router.get("/daily-work-orders")
def get_daily_work_orders():

    return get_work_orders_service()