from fastapi import FastAPI

from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../db")
    )
)

from models import DailyWorkOrder, DailyReport

from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

DATABASE_URL = "postgresql://postgres:Mahshid88@localhost:5433/betavanx_db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

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

     # 🔹 1. خواندن task data
    tasks_df = pd.read_excel("../data/raw/betavanx_mvp_v1.xlsx")

    # 🔹 2. خواندن گزارش کار
    reports_df = pd.read_excel("../data/raw/work_report.xlsx")
    
    # 🔹 3. خواندن گزارش هزینه
    cost_df = pd.read_excel("../data/raw/cost_report.xlsx")

    # 🔹 3. merge
    df = tasks_df.merge(
        reports_df,
        left_on="id",
        right_on="task_id",
        how="left"
    )
    df = df.merge(
        cost_df,
        left_on="id",
        right_on="task_id",
        how="left"
    )
    print(df.columns)
    # 🔹 2. ساخت دیتا تستی شبیه چیزی که قبلاً داشتی
    df["progress_percent"] = (
        df["executed_qty"] / df["baseline_qty"]
    ) * 100

    # 🔹 planned progress
    df["planned_progress"] = 50

    df["planned_cost"] = df["budget"]

    # 🔹 3. محاسبه expected cost
    df["expected_cost"] = df["planned_cost"] * (df["progress_percent"] / 100)
    # 🔹 CPI
    df["cpi"] = df["expected_cost"] / df["actual_cost"]

    # 🔹 SPI
    df["spi"] = df["progress_percent"] / df["planned_progress"]

    # 🔹 Decision Score
    df["final_score"] = (
        (df["cpi"] * 40) +
        (df["spi"] * 40) +
        (df["progress_percent"] * 0.2)
    )
    print(df[[
        "progress_percent",
        "cpi",
        "spi",
        "final_score"
    ]])
    # 🔹 Risk Score
    df["risk_score"] = 100 - df["final_score"]

    # 🔹 5. alert
    def get_alert(score):

        if score < 60:
            return "🔴 Critical"

        elif score < 80:
            return "🟡 Warning"

        else:
            return "🟢 Good"

    def get_risk_level(risk):

        if risk > 60:
            return "🔴 High Risk"

        elif risk > 30:
            return "🟡 Medium Risk"

        else:
            return "🟢 Low Risk"

    df["alert"] = df["final_score"].apply(get_alert)

    df["risk_level"] = df["risk_score"].apply(get_risk_level)

    # 🔹 6. انتخاب ستون‌ها
    result = df.rename(columns={"id": "task_id"})[
    [
        "task_id",
        "progress_percent",
        "planned_progress",
        "final_score",
        "cpi",
        "spi",
        "alert",
        "risk_score",
        "risk_level",
    ]
]

    # 🔹 7. تبدیل به JSON
    return result.to_dict(orient="records")


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