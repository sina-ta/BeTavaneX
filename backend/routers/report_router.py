from fastapi import APIRouter

from backend.database import SessionLocal

from backend.schemas import DailyReportCreate

from backend.repositories.task_repository import (
    TaskRepository,
)

from backend.services.report_service import (
    create_daily_report_service,
    get_reports_service,
)

router = APIRouter()


@router.post("/daily-report")
def create_daily_report(report: DailyReportCreate):
    session = SessionLocal()

    try:
        task_repo = TaskRepository(session)

        work_order = task_repo.get_work_order_by_id(
            report.work_order_id,
        )

        return create_daily_report_service(
            report,
            work_order,
        )

    finally:
        session.close()


@router.get("/daily-reports")
def get_daily_reports():
    return get_reports_service()
