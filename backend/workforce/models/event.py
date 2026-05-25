from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from datetime import datetime

from backend.models.main_models import Base


class WorkforceEvent(Base):
    __tablename__ = "workforce_events"

    id = Column(Integer, primary_key=True)
    worker_id = Column(Integer, ForeignKey("workforce_workers.id"))
    crew_id = Column(Integer, ForeignKey("workforce_crews.id"))
    event_type = Column(String(80), nullable=False)
    severity = Column(String(40))
    source = Column(String(60))
    occurred_at = Column(DateTime, default=datetime.utcnow)
    payload = Column(Text)
