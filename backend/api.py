from fastapi import FastAPI
from pydantic import BaseModel

from backend.database import SessionLocal, engine

from backend.models import (
    Base,
    DailyWorkOrder,
    DailyReport
)

from backend.services.kpi_engine import calculate_kpis

from backend.services.interpretation_engine import (
    interpret_project,
    generate_recommendation
)

from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

Base.metadata.create_all(bind=engine)

# ✅ CORS (برای اتصال React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class WorkOrderCreate(BaseModel):

    project_id: int

    task_id: int

    assigned_to: str

    planned_qty: float

    unit: str

    priority: str

    status: str

    created_by: str

class DailyReportCreate(BaseModel):

    work_order_id: int

    reported_by: str

    actual_qty: float

    manpower_count: int

    equipment_hours: float

    material_consumption: float

    delay_reason: str

    weather_status: str

    photo_count: int

    report_status: str

    approved_by: str


@app.get("/dashboard")
def get_dashboard():

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

        kpis = calculate_kpis(wo, reports)

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

@app.post("/daily-work-order")

def create_work_order(work_order: WorkOrderCreate):

    session = SessionLocal()

    new_work_order = DailyWorkOrder(

        project_id=work_order.project_id,

        task_id=work_order.task_id,

        assigned_to=work_order.assigned_to,

        planned_qty=work_order.planned_qty,

        unit=work_order.unit,

        priority=work_order.priority,

        status=work_order.status,

        created_by=work_order.created_by
    )

    session.add(new_work_order)

    session.commit()

    return {
        "message": "✅ Work Order Created"
    }
@app.get("/daily-work-orders")

def get_daily_work_orders():

    session = SessionLocal()

    work_orders = session.query(DailyWorkOrder).all()

    result = []

    for wo in work_orders:

        result.append({
            "id": wo.id,
            "project_id": wo.project_id,
            "task_id": wo.task_id,
            "assigned_to": wo.assigned_to,
            "planned_qty": wo.planned_qty,
            "unit": wo.unit,
            "priority": wo.priority,
            "status": wo.status,
            "created_by": wo.created_by
        })

    return result
    

@app.post("/daily-report")

def create_daily_report(report: DailyReportCreate):

    session = SessionLocal()

     # =========================
    # Validation Engine v1
    # =========================

    validation_warnings = []

    # 🔹 Find related work order
    work_order = session.query(DailyWorkOrder).filter(
        DailyWorkOrder.id == report.work_order_id
    ).first()

    # 🔹 Rule 1
    if not work_order:

        validation_warnings.append(
            "⚠️ Invalid Work Order ID"
        )

    else:

        if report.actual_qty > work_order.planned_qty:

            validation_warnings.append(
                "⚠️ Actual quantity exceeds planned quantity"
            )

    # 🔹 Rule 2
    if report.manpower_count > 20:

        validation_warnings.append(
            "⚠️ Suspicious manpower allocation"
        )

    # 🔹 Rule 3
    if report.actual_qty < 5 and report.delay_reason == "None":

        validation_warnings.append(
            "⚠️ Low progress without delay reason"
        )

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