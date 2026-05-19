from backend.database import SessionLocal

from backend.models import DailyReport


def create_daily_report_service(
    report,
    validation_warnings
):

    session = SessionLocal()

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

        approved_by=report.approved_by
    )

    session.add(new_report)

    session.commit()

    return {

        "message": "✅ Daily Report Created",

        "validation_warnings": validation_warnings
    }


def get_reports_service():

    session = SessionLocal()

    reports = session.query(
        DailyReport
    ).all()

    result = []

    for report in reports:

        result.append({

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

            "approved_by": report.approved_by
        })

    return result