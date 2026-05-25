from sqlalchemy import Column, Integer, String

from backend.models.main_models import Base


class MedicalStatus(Base):
    __tablename__ = "workforce_medical_statuses"

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False, unique=True)
    clearance_level = Column(String(40))
    description = Column(String)
