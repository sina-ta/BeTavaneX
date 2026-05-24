from sqlalchemy.orm import Session

from backend.models import DailyWorkOrder, DailyReport


class DashboardRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all_work_orders(self) -> list[DailyWorkOrder]:
        return self.session.query(DailyWorkOrder).all()

    def get_all_reports(self) -> list[DailyReport]:
        return self.session.query(DailyReport).all()

    def filter_reports_for_work_order(
        self,
        work_order_id: int,
        reports: list[DailyReport],
    ) -> list[DailyReport]:
        return [
            report
            for report in reports
            if report.work_order_id == work_order_id
        ]
