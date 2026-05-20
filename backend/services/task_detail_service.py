from backend.database import SessionLocal

from backend.models import (
    DailyWorkOrder,
    DailyReport
)

from backend.services.kpi_engine import calculate_kpis

from backend.services.interpretation_engine import (
    interpret_project,
    generate_recommendation
)


def get_task_detail_service(task_id):

    session = SessionLocal()

    # =========================
    # Find Work Order
    # =========================

    work_order = session.query(
        DailyWorkOrder
    ).filter(
        DailyWorkOrder.task_id == task_id
    ).first()

    if not work_order:

        return {
            "error": "Task not found"
        }

    # =========================
    # Related Reports
    # =========================

    reports = session.query(
        DailyReport
    ).filter(
        DailyReport.work_order_id == work_order.id
    ).all()

    # =========================
    # KPI Calculation
    # =========================

    kpis = calculate_kpis(
        work_order,
        reports
    )

    interpretation = interpret_project(
        kpis["cpi"],
        kpis["spi"],
        kpis["final_score"],
        kpis["risk_score"]
    )

    recommendation = generate_recommendation(
        kpis["cpi"],
        kpis["spi"]
    )

    # =========================
    # Report Serialization
    # =========================

    serialized_reports = []

    for report in reports:

        serialized_reports.append({

            "id": report.id,

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

    return {

        "task_id": work_order.task_id,

        "assigned_to": work_order.assigned_to,

        "planned_qty": work_order.planned_qty,

        "status": work_order.status,

        **kpis,

        **interpretation,

        "recommendation": recommendation,

        "reports": serialized_reports
    }