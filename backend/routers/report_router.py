from fastapi import APIRouter

from backend.database import SessionLocal

from backend.models import (
    DailyWorkOrder,
    DailyReport
)

from backend.schemas import DailyReportCreate

from backend.services.validation_engine import (
    validate_daily_report
)

from backend.services.report_service import (
    create_daily_report_service,
    get_reports_service
)

router = APIRouter()


@router.post("/daily-report")
def create_daily_report(report: DailyReportCreate):

    session = SessionLocal()

    # =========================
    # Find Related Work Order
    # =========================

    work_order = session.query(DailyWorkOrder).filter(
        DailyWorkOrder.id == report.work_order_id
    ).first()

    # =========================
    # Validation Engine
    # =========================

    validation_warnings = validate_daily_report(
        report,
        work_order
    )

    return create_daily_report_service(
        report,
        validation_warnings
    )

@router.get("/daily-reports")
def get_daily_reports():

    return get_reports_service()