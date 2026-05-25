from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from backend.models.main_models import Base


class Crew(Base):
    __tablename__ = "workforce_crews"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    trade = Column(String(80))
    supervisor = Column(String(120))
    active_project_id = Column(Integer)
    performance_score = Column(Float)
    utilization_rate = Column(Float)

    workers = relationship("Worker", back_populates="crew")
