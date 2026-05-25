from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime
from datetime import datetime

from backend.models.main_models import Base


class WorkerAvailability(Base):
    __tablename__ = "workforce_availability"

    id = Column(Integer, primary_key=True)
    worker_id = Column(
        Integer,
        ForeignKey("workforce_workers.id"),
        nullable=False,
    )
    status = Column(String(40), nullable=False)
    effective_from = Column(DateTime, default=datetime.utcnow)
    effective_until = Column(DateTime)
    reason = Column(String)
