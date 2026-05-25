from fastapi import APIRouter

from backend.schemas import DailyReportCreate

from backend.validation.services.validation_service import (
    get_validation_summary_service,
    get_report_validation_service,
    get_active_anomalies_service,
    preview_daily_report_validation,
)

router = APIRouter(
    prefix="/validation",
    tags=["validation"],
)


@router.get("/summary")
def validation_summary():
    return get_validation_summary_service()


@router.get("/anomalies")
def active_anomalies():
    return get_active_anomalies_service()


@router.get("/reports/{report_id}")
def report_validation(report_id: int):
    return get_report_validation_service(report_id)


@router.post("/reports/preview")
def preview_report_validation(report: DailyReportCreate):
    return preview_daily_report_validation(
        report,
        report.work_order_id,
    )
