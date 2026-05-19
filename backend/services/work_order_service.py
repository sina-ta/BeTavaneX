from backend.database import SessionLocal

from backend.models import DailyWorkOrder


def create_work_order_service(work_order):

    session = SessionLocal()

    new_work_order = DailyWorkOrder(

        project_id=work_order.project_id,

        task_id=work_order.task_id,

        assigned_to=work_order.assigned_to,

        planned_qty=work_order.planned_qty,

        unit=work_order.unit,

        priority=work_order.priority,

        status=work_order.status,

        created_by=work_order.created_by
    )

    session.add(new_work_order)

    session.commit()

    return {
        "message": "✅ Work Order Created"
    }


def get_work_orders_service():

    session = SessionLocal()

    work_orders = session.query(
        DailyWorkOrder
    ).all()

    result = []

    for wo in work_orders:

        result.append({

            "id": wo.id,

            "project_id": wo.project_id,

            "task_id": wo.task_id,

            "assigned_to": wo.assigned_to,

            "planned_qty": wo.planned_qty,

            "unit": wo.unit,

            "priority": wo.priority,

            "status": wo.status,

            "created_by": wo.created_by
        })

    return result