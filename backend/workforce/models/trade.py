from sqlalchemy import Column, Integer, String, Text

from backend.models.main_models import Base


class Trade(Base):
    __tablename__ = "workforce_trades"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False, unique=True)
    description = Column(Text)
