from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    ForeignKey,
    Date,
    DateTime,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.models.main_models import Base


class Worker(Base):
    __tablename__ = "workforce_workers"

    id = Column(Integer, primary_key=True)

    # Identity
    first_name = Column(String(80), nullable=False)
    last_name = Column(String(80), nullable=False)
    national_id = Column(String(40), unique=True)
    phone = Column(String(40))
    emergency_contact = Column(String(120))
    profile_photo = Column(String)

    # Operational
    trade_id = Column(Integer, ForeignKey("workforce_trades.id"))
    current_role = Column(String(80))
    skill_level = Column(String(40))
    availability_status = Column(String(40), default="available")
    current_project_id = Column(Integer)
    current_crew_id = Column(Integer, ForeignKey("workforce_crews.id"))

    # Employment
    employment_type = Column(String(40))
    hire_date = Column(Date)
    contract_type = Column(String(40))
    daily_cost = Column(Float)
    payroll_group = Column(String(80))

    # Compliance
    medical_status_id = Column(
        Integer,
        ForeignKey("workforce_medical_statuses.id"),
    )
    insurance_status = Column(String(40))
    safety_clearance = Column(String(40))

    # Logistics
    accommodation_required = Column(Boolean, default=False)
    transportation_required = Column(Boolean, default=False)
    home_city = Column(String(80))
    current_location = Column(String(120))

    # Scoring — derived from operational data, not manually set
    productivity_score = Column(Float)
    reliability_score = Column(Float)
    safety_score = Column(Float)
    teamwork_score = Column(Float)
    quality_score = Column(Float)
    leadership_score = Column(Float)

    # System
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    trade = relationship("Trade")
    crew = relationship("Crew", back_populates="workers")
    medical_status = relationship("MedicalStatus")
    skills = relationship("WorkerSkill", back_populates="worker")
    certifications = relationship(
        "WorkerCertification",
        back_populates="worker",
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
