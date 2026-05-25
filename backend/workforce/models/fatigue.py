from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from datetime import datetime

from backend.models.main_models import Base


class WorkerFatigue(Base):
    __tablename__ = "workforce_fatigue"

    id = Column(Integer, primary_key=True)
    worker_id = Column(
        Integer,
        ForeignKey("workforce_workers.id"),
        nullable=False,
    )
    fatigue_level = Column(Float)
    readiness_score = Column(Float)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    source = Column(String(60), default="manual")
    notes = Column(String)
