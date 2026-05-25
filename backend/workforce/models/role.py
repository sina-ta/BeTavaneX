from sqlalchemy import Column, Integer, String, Text

from backend.models.main_models import Base


class OperationalRole(Base):
    __tablename__ = "workforce_operational_roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False, unique=True)
    authority_level = Column(Integer, default=1)
    description = Column(Text)
