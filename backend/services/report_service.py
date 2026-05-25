from backend.database import SessionLocal

from backend.models import DailyReport

from backend.repositories.report_repository import (
    ReportRepository,
)

from backend.validation.services.validation_service import (
    validate_and_persist_daily_report,
)


def create_daily_report_service(report, work_order):
    session = SessionLocal()

    try:
        repo = ReportRepository(session)

        new_report = DailyReport(
            work_order_id=report.work_order_id,
            reported_by=report.reported_by,
            actual_qty=report.actual_qty,
            manpower_count=report.manpower_count,
            equipment_hours=report.equipment_hours,
            material_consumption=report.material_consumption,
            delay_reason=report.delay_reason,
            weather_status=report.weather_status,
            photo_count=report.photo_count,
            report_status=report.report_status,
            approved_by=report.approved_by,
        )

        created = repo.create(new_report)

        validation = validate_and_persist_daily_report(
            report,
            work_order,
            created.id,
        )

        return {
            "message": "✅ Daily Report Created",
            "report_id": created.id,
            "validation": validation,
            "validation_warnings": validation["warnings"],
            "trusted": validation["trusted"],
            "trust_score": validation["trust_score"],
        }

    finally:
        session.close()


def get_reports_service():
    session = SessionLocal()

    try:
        repo = ReportRepository(session)
        reports = repo.get_all()

        return [
            {
                "id": report.id,
                "work_order_id": report.work_order_id,
                "reported_by": report.reported_by,
                "actual_qty": report.actual_qty,
                "manpower_count": report.manpower_count,
                "equipment_hours": report.equipment_hours,
                "material_consumption": report.material_consumption,
                "delay_reason": report.delay_reason,
                "weather_status": report.weather_status,
                "photo_count": report.photo_count,
                "report_status": report.report_status,
                "approved_by": report.approved_by,
            }
            for report in reports
        ]

    finally:
        session.close()
