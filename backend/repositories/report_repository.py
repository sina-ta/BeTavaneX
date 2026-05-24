from sqlalchemy.orm import Session

from backend.models import DailyReport


class ReportRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[DailyReport]:
        return self.session.query(DailyReport).all()

    def get_by_work_order_id(
        self,
        work_order_id: int,
    ) -> list[DailyReport]:
        return (
            self.session.query(DailyReport)
            .filter(DailyReport.work_order_id == work_order_id)
            .all()
        )

    def create(self, report: DailyReport) -> DailyReport:
        self.session.add(report)
        self.session.commit()
        self.session.refresh(report)
        return report
