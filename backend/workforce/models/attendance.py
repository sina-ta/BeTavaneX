from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date

from backend.models.main_models import Base


class Attendance(Base):
    __tablename__ = "workforce_attendance"

    id = Column(Integer, primary_key=True)
    worker_id = Column(
        Integer,
        ForeignKey("workforce_workers.id"),
        nullable=False,
    )
    date = Column(Date, nullable=False)
    shift = Column(String(40))
    check_in = Column(String(20))
    check_out = Column(String(20))
    status = Column(String(40))
    overtime_hours = Column(Float, default=0)
    absence_reason = Column(String)
