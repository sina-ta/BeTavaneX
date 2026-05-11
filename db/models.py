from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Text,
    TIMESTAMP,
    ForeignKey
)

from sqlalchemy.orm import declarative_base

Base = declarative_base()


# =========================
# Daily Work Orders
# =========================

class DailyWorkOrder(Base):

    __tablename__ = "daily_work_orders"

    id = Column(Integer, primary_key=True)

    project_id = Column(Integer)

    task_id = Column(Integer)

    assigned_to = Column(String(100))

    planned_qty = Column(Float)

    unit = Column(String(20))

    planned_start = Column(TIMESTAMP)

    planned_finish = Column(TIMESTAMP)

    priority = Column(String(20))

    status = Column(String(20))

    created_by = Column(String(100))

    created_at = Column(TIMESTAMP)


# =========================
# Daily Reports
# =========================

class DailyReport(Base):

    __tablename__ = "daily_reports"

    id = Column(Integer, primary_key=True)

    work_order_id = Column(
        Integer,
        ForeignKey("daily_work_orders.id")
    )

    reported_by = Column(String(100))

    actual_qty = Column(Float)

    manpower_count = Column(Integer)

    equipment_hours = Column(Float)

    material_consumption = Column(Float)

    delay_reason = Column(Text)

    weather_status = Column(String(50))

    photo_count = Column(Integer)

    report_status = Column(String(20))

    submitted_at = Column(TIMESTAMP)

    approved_by = Column(String(100))