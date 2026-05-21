from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    Date,
    DateTime
)

from sqlalchemy.orm import relationship

from backend.models import Base


# =========================
# Roles
# =========================

class Role(Base):

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)

    title = Column(String)


# =========================
# Crews
# =========================

class Crew(Base):

    __tablename__ = "crews"

    id = Column(Integer, primary_key=True)

    name = Column(String)

    description = Column(String)


# =========================
# Workers
# =========================

class Worker(Base):

    __tablename__ = "workers"

    id = Column(Integer, primary_key=True)

    full_name = Column(String)

    phone = Column(String)

    national_id = Column(String)

    role_id = Column(
        Integer,
        ForeignKey("roles.id")
    )

    crew_id = Column(
        Integer,
        ForeignKey("crews.id")
    )

    join_date = Column(Date)

    status = Column(String)

    daily_wage = Column(Float)

    score = Column(Float)

    avatar = Column(String)

    role = relationship("Role")

    crew = relationship("Crew")

    # =========================
# Skills
# =========================

class Skill(Base):

    __tablename__ = "skills"

    id = Column(Integer, primary_key=True)

    title = Column(String)


# =========================
# Worker Skills
# =========================

class WorkerSkill(Base):

    __tablename__ = "worker_skills"

    id = Column(Integer, primary_key=True)

    worker_id = Column(
        Integer,
        ForeignKey("workers.id")
    )

    skill_id = Column(
        Integer,
        ForeignKey("skills.id")
    )

    skill_level = Column(String)

    experience_years = Column(Float)

    worker = relationship("Worker")

    skill = relationship("Skill")

    # =========================
# Worker Attendance
# =========================

class WorkerAttendance(Base):

    __tablename__ = "worker_attendance"

    id = Column(Integer, primary_key=True)

    worker_id = Column(
        Integer,
        ForeignKey("workers.id")
    )

    date = Column(Date)

    check_in = Column(String)

    check_out = Column(String)

    status = Column(String)

    work_hours = Column(Float)

    overtime_hours = Column(Float)

    worker = relationship("Worker")

    # =========================
# Worker Payments
# =========================

class WorkerPayment(Base):

    __tablename__ = "worker_payments"

    id = Column(Integer, primary_key=True)

    worker_id = Column(
        Integer,
        ForeignKey("workers.id")
    )

    amount = Column(Float)

    payment_type = Column(String)

    payment_date = Column(Date)

    description = Column(String)

    worker = relationship("Worker")

    # =========================
# Worker Scores
# =========================

class WorkerScore(Base):

    __tablename__ = "worker_scores"

    id = Column(Integer, primary_key=True)

    worker_id = Column(
        Integer,
        ForeignKey("workers.id")
    )

    productivity_score = Column(Float)

    quality_score = Column(Float)

    safety_score = Column(Float)

    discipline_score = Column(Float)

    final_score = Column(Float)

    score_date = Column(Date)

    worker = relationship("Worker")

    # =========================
# Task Assignments
# =========================

class TaskAssignment(Base):

    __tablename__ = "task_assignments"

    id = Column(Integer, primary_key=True)

    worker_id = Column(
        Integer,
        ForeignKey("workers.id")
    )

    work_order_id = Column(
        Integer,
        ForeignKey("daily_work_orders.id")
    )

    assigned_date = Column(Date)

    assigned_by = Column(String)

    status = Column(String)

    worker = relationship("Worker")

    # =========================
# Worker Training
# =========================

class WorkerTraining(Base):

    __tablename__ = "worker_training"

    id = Column(Integer, primary_key=True)

    worker_id = Column(
        Integer,
        ForeignKey("workers.id")
    )

    title = Column(String)

    status = Column(String)

    completed_at = Column(Date)

    certificate_file = Column(String)

    worker = relationship("Worker")


# =========================
# Worker Certificates
# =========================

class WorkerCertificate(Base):

    __tablename__ = "worker_certificates"

    id = Column(Integer, primary_key=True)

    worker_id = Column(
        Integer,
        ForeignKey("workers.id")
    )

    certificate_name = Column(String)

    expire_date = Column(Date)

    status = Column(String)

    worker = relationship("Worker")

    # =========================
# Worker Equipment
# =========================

class WorkerEquipment(Base):

    __tablename__ = "worker_equipment"

    id = Column(Integer, primary_key=True)

    worker_id = Column(
        Integer,
        ForeignKey("workers.id")
    )

    equipment_name = Column(String)

    delivery_date = Column(Date)

    return_date = Column(Date)

    status = Column(String)

    worker = relationship("Worker")

    