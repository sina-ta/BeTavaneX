from backend.database import SessionLocal

from backend.repositories.dashboard_repository import (
    DashboardRepository,
)

from backend.services.kpi_engine import calculate_kpis

from backend.services.interpretation_engine import (
    interpret_project,
)

from backend.services.recommendations.generator import (
    generate_recommendations,
)

from backend.services.analytics_service import (
    record_dashboard_kpis,
    get_project_kpi_trends,
)


def build_dashboard():
    session = SessionLocal()

    try:
        repo = DashboardRepository(session)

        work_orders = repo.get_all_work_orders()
        reports = repo.get_all_reports()

        dashboard_data = []

        for work_order in work_orders:
            related_reports = repo.filter_reports_for_work_order(
                work_order.id,
                reports,
            )

            kpis = calculate_kpis(
                work_order,
                related_reports,
            )

            interpretation = interpret_project(
                kpis["cpi"],
                kpis["spi"],
                kpis["final_score"],
                kpis["risk_score"],
            )

            workforce_count = sum(
                report.manpower_count or 0
                for report in related_reports
            )

            recommendation = generate_recommendations(
                cpi=kpis["cpi"],
                spi=kpis["spi"],
                progress_percent=kpis["progress_percent"],
                final_score=kpis["final_score"],
                risk_score=kpis["risk_score"],
                workforce_count=workforce_count,
            )

            dashboard_data.append({
                "task_id": work_order.task_id,
                **kpis,
                **interpretation,
                "recommendation": recommendation,
            })

        task_count = len(dashboard_data)

        summary = {
            "total_work_orders": len(work_orders),
            "total_reports": len(reports),
            "avg_cpi": round(
                sum(item["cpi"] for item in dashboard_data)
                / task_count,
                2,
            )
            if task_count
            else 0,
            "avg_spi": round(
                sum(item["spi"] for item in dashboard_data)
                / task_count,
                2,
            )
            if task_count
            else 0,
            "critical_alerts": len([
                item
                for item in dashboard_data
                if item["alert"] == "🔴 Critical"
            ]),
            "warning_alerts": len([
                item
                for item in dashboard_data
                if item["alert"] == "🟡 Warning"
            ]),
        }

        if dashboard_data:
            record_dashboard_kpis(dashboard_data)

        trends = get_project_kpi_trends()

        return {
            "summary": summary,
            "tasks": dashboard_data,
            "trends": trends,
        }

    finally:
        session.close()
