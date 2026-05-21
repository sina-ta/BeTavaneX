from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float

Base = declarative_base()


class DailyWorkOrder(Base):

    __tablename__ = "daily_work_orders"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(Integer)

    task_id = Column(Integer, unique=True)

    assigned_to = Column(String)

    planned_qty = Column(Float)

    unit = Column(String)

    priority = Column(String)

    status = Column(String)

    created_by = Column(String)


class DailyReport(Base):

    __tablename__ = "daily_reports"

    id = Column(Integer, primary_key=True, index=True)

    work_order_id = Column(Integer)

    reported_by = Column(String)

    actual_qty = Column(Float)

    manpower_count = Column(Integer)

    equipment_hours = Column(Float)

    material_consumption = Column(Float)

    delay_reason = Column(String)

    weather_status = Column(String)

    photo_count = Column(Integer)

    report_status = Column(String)

    approved_by = Column(String)