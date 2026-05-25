from sqlalchemy import Column, Integer, String, ForeignKey, Date

from backend.models.main_models import Base


class Accommodation(Base):
    __tablename__ = "workforce_accommodations"

    id = Column(Integer, primary_key=True)
    worker_id = Column(
        Integer,
        ForeignKey("workforce_workers.id"),
        nullable=False,
    )
    location = Column(String(160))
    status = Column(String(40))
    check_in_date = Column(Date)
    check_out_date = Column(Date)
