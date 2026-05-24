from sqlalchemy.orm import Session

from backend.models import DailyWorkOrder, DailyReport


class TaskRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all_work_orders(self) -> list[DailyWorkOrder]:
        return self.session.query(DailyWorkOrder).all()

    def get_work_order_by_task_id(
        self,
        task_id: int,
    ) -> DailyWorkOrder | None:
        return (
            self.session.query(DailyWorkOrder)
            .filter(DailyWorkOrder.task_id == task_id)
            .first()
        )

    def get_work_order_by_id(
        self,
        work_order_id: int,
    ) -> DailyWorkOrder | None:
        return (
            self.session.query(DailyWorkOrder)
            .filter(DailyWorkOrder.id == work_order_id)
            .first()
        )

    def create_work_order(
        self,
        work_order: DailyWorkOrder,
    ) -> DailyWorkOrder:
        self.session.add(work_order)
        self.session.commit()
        self.session.refresh(work_order)
        return work_order
