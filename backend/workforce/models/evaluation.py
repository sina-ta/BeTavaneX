from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Text

from backend.models.main_models import Base


class WorkerEvaluation(Base):
    __tablename__ = "workforce_evaluations"

    id = Column(Integer, primary_key=True)
    worker_id = Column(
        Integer,
        ForeignKey("workforce_workers.id"),
        nullable=False,
    )
    evaluator = Column(String(120))
    evaluation_source = Column(String(60))
    evaluation_date = Column(Date)
    productivity = Column(Float)
    reliability = Column(Float)
    quality = Column(Float)
    safety = Column(Float)
    teamwork = Column(Float)
    discipline = Column(Float)
    leadership = Column(Float)
    operational_notes = Column(Text)
