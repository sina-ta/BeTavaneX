from backend.database import SessionLocal

from backend.models import DailyWorkOrder

from backend.repositories.task_repository import (
    TaskRepository,
)


def create_work_order_service(work_order):
    session = SessionLocal()

    try:
        repo = TaskRepository(session)

        new_work_order = DailyWorkOrder(
            project_id=work_order.project_id,
            task_id=work_order.task_id,
            assigned_to=work_order.assigned_to,
            planned_qty=work_order.planned_qty,
            unit=work_order.unit,
            priority=work_order.priority,
            status=work_order.status,
            created_by=work_order.created_by,
        )

        repo.create_work_order(new_work_order)

        return {
            "message": "✅ Work Order Created",
        }

    finally:
        session.close()


def get_work_orders_service():
    session = SessionLocal()

    try:
        repo = TaskRepository(session)
        work_orders = repo.get_all_work_orders()

        return [
            {
                "id": work_order.id,
                "project_id": work_order.project_id,
                "task_id": work_order.task_id,
                "assigned_to": work_order.assigned_to,
                "planned_qty": work_order.planned_qty,
                "unit": work_order.unit,
                "priority": work_order.priority,
                "status": work_order.status,
                "created_by": work_order.created_by,
            }
            for work_order in work_orders
        ]

    finally:
        session.close()
