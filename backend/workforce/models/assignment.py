from sqlalchemy import Column, Integer, String, ForeignKey, Date

from backend.models.main_models import Base


class Assignment(Base):
    __tablename__ = "workforce_assignments"

    id = Column(Integer, primary_key=True)
    worker_id = Column(
        Integer,
        ForeignKey("workforce_workers.id"),
        nullable=False,
    )
    work_order_id = Column(Integer)
    task_id = Column(Integer)
    crew_id = Column(Integer, ForeignKey("workforce_crews.id"))
    project_id = Column(Integer)
    assigned_date = Column(Date)
    assigned_by = Column(String(120))
    status = Column(String(40), default="assigned")
    readiness_status = Column(String(40))
