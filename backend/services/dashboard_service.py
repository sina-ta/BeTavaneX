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

def build_dashboard():

    session = SessionLocal()

    work_orders = session.query(DailyWorkOrder).all()

    reports = session.query(DailyReport).all()

    dashboard_data = []

    # =========================
    # KPI Engine from DB
    # =========================

    for wo in work_orders:

        related_reports = [
            r for r in reports
            if r.work_order_id == wo.id
        ]

        kpis = calculate_kpis(
            wo,
            related_reports
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


        dashboard_data.append({

            "task_id": wo.task_id,

             **kpis,

            **interpretation,

            "recommendation": recommendation,
         })

        summary = {

            "total_work_orders": len(work_orders),

            "total_reports": len(reports),

            "avg_cpi": round(
                sum(item["cpi"] for item in dashboard_data)
                / len(dashboard_data),
                2
            ),

            "avg_spi": round(
                sum(item["spi"] for item in dashboard_data)
                / len(dashboard_data),
                2
            ),

            "critical_alerts": len([
                item for item in dashboard_data
                if item["alert"] == "🔴 Critical"
            ]),

            "warning_alerts": len([
                item for item in dashboard_data
                if item["alert"] == "🟡 Warning"
            ])
        }
                

    return {
    "summary": summary,
    "tasks": dashboard_data
    }