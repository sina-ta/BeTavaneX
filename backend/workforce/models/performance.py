from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from datetime import datetime

from backend.models.main_models import Base


class PerformanceMetric(Base):
    __tablename__ = "workforce_performance_metrics"

    id = Column(Integer, primary_key=True)
    worker_id = Column(
        Integer,
        ForeignKey("workforce_workers.id"),
        nullable=False,
    )
    work_order_id = Column(Integer)
    daily_report_id = Column(Integer)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    metric_type = Column(String(60), nullable=False)
    metric_value = Column(Float)
    source = Column(String(60), default="daily_report")
    notes = Column(String)
