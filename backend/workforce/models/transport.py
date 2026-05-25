from sqlalchemy import Column, Integer, String, ForeignKey, Date

from backend.models.main_models import Base


class Transport(Base):
    __tablename__ = "workforce_transport"

    id = Column(Integer, primary_key=True)
    worker_id = Column(
        Integer,
        ForeignKey("workforce_workers.id"),
        nullable=False,
    )
    transport_type = Column(String(80))
    route = Column(String(160))
    status = Column(String(40))
    assigned_date = Column(Date)
