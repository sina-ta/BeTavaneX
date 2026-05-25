from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date

from backend.models.main_models import Base


class Contract(Base):
    __tablename__ = "workforce_contracts"

    id = Column(Integer, primary_key=True)
    worker_id = Column(
        Integer,
        ForeignKey("workforce_workers.id"),
        nullable=False,
    )
    contract_type = Column(String(40))
    start_date = Column(Date)
    end_date = Column(Date)
    daily_rate = Column(Float)
    status = Column(String(40))
