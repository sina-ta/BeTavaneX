from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    Date,
)
from sqlalchemy.orm import relationship

from backend.models.main_models import Base


class Skill(Base):
    __tablename__ = "workforce_skills"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False, unique=True)
    category = Column(String(80))
    description = Column(String)


class WorkerSkill(Base):
    __tablename__ = "workforce_worker_skills"

    id = Column(Integer, primary_key=True)
    worker_id = Column(
        Integer,
        ForeignKey("workforce_workers.id"),
        nullable=False,
    )
    skill_id = Column(
        Integer,
        ForeignKey("workforce_skills.id"),
        nullable=False,
    )
    proficiency_level = Column(String(40))
    experience_years = Column(Float)

    worker = relationship("Worker", back_populates="skills")
    skill = relationship("Skill")


class Certification(Base):
    __tablename__ = "workforce_certifications"

    id = Column(Integer, primary_key=True)
    name = Column(String(160), nullable=False, unique=True)
    issuing_authority = Column(String(160))
    description = Column(String)


class WorkerCertification(Base):
    __tablename__ = "workforce_worker_certifications"

    id = Column(Integer, primary_key=True)
    worker_id = Column(
        Integer,
        ForeignKey("workforce_workers.id"),
        nullable=False,
    )
    certification_id = Column(
        Integer,
        ForeignKey("workforce_certifications.id"),
        nullable=False,
    )
    issue_date = Column(Date)
    expiry_date = Column(Date)
    status = Column(String(40), default="active")

    worker = relationship("Worker", back_populates="certifications")
    certification = relationship("Certification")
