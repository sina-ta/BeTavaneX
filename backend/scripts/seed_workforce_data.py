"""Seed operational workforce foundation data."""

from datetime import date, timedelta

from backend.database import SessionLocal, engine

from backend.models.main_models import Base

import backend.workforce.models  # noqa: F401 — register tables

from backend.workforce.models.trade import Trade
from backend.workforce.models.skill import (
    Skill,
    WorkerSkill,
    Certification,
    WorkerCertification,
)
from backend.workforce.models.medical import MedicalStatus
from backend.workforce.models.crew import Crew
from backend.workforce.models.worker import Worker
from backend.workforce.models.role import OperationalRole
from backend.workforce.models.attendance import Attendance
from backend.workforce.models.assignment import Assignment


def seed():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()

    try:
        if session.query(Worker).count() > 0:
            print("Workforce data already seeded.")
            return

        roles = [
            OperationalRole(name="Worker", authority_level=1),
            OperationalRole(name="Crew Lead", authority_level=2),
            OperationalRole(name="Supervisor", authority_level=3),
            OperationalRole(name="Senior Field Validator", authority_level=4),
            OperationalRole(name="Project Manager", authority_level=5),
            OperationalRole(name="Operations Manager", authority_level=6),
        ]
        session.add_all(roles)

        trades = [
            Trade(name="Concrete"),
            Trade(name="Formwork"),
            Trade(name="Rebar"),
            Trade(name="MEP"),
        ]
        session.add_all(trades)
        session.flush()

        medical = MedicalStatus(
            name="Cleared",
            clearance_level="full",
            description="Fit for field operations",
        )
        session.add(medical)
        session.flush()

        skills = [
            Skill(name="Concrete pouring", category="concrete"),
            Skill(name="Formwork installation", category="formwork"),
            Skill(name="Rebar tying", category="rebar"),
            Skill(name="Crane operation", category="equipment"),
        ]
        session.add_all(skills)
        session.flush()

        certs = [
            Certification(
                name="Safety Training",
                issuing_authority="Site Safety Board",
            ),
            Certification(
                name="Crane Operator License",
                issuing_authority="Heavy Equipment Authority",
            ),
        ]
        session.add_all(certs)
        session.flush()

        crews = [
            Crew(
                name="Crew Alpha",
                trade="Concrete",
                supervisor="A. Karimi",
                active_project_id=1,
                performance_score=82,
                utilization_rate=76,
            ),
            Crew(
                name="Crew Beta",
                trade="Rebar",
                supervisor="M. Hosseini",
                active_project_id=1,
                performance_score=74,
                utilization_rate=68,
            ),
        ]
        session.add_all(crews)
        session.flush()

        workers = [
            Worker(
                first_name="Ali",
                last_name="Rezaei",
                national_id="0012345678",
                phone="09120000001",
                trade_id=trades[0].id,
                current_role="Crew Lead",
                skill_level="senior",
                availability_status="assigned",
                current_crew_id=crews[0].id,
                current_project_id=1,
                employment_type="contract",
                hire_date=date(2024, 3, 1),
                daily_cost=850000,
                medical_status_id=medical.id,
                insurance_status="active",
                safety_clearance="cleared",
                productivity_score=84,
                reliability_score=88,
                safety_score=90,
                teamwork_score=86,
                quality_score=82,
                leadership_score=80,
            ),
            Worker(
                first_name="Hassan",
                last_name="Moradi",
                national_id="0012345679",
                phone="09120000002",
                trade_id=trades[2].id,
                current_role="Worker",
                skill_level="mid",
                availability_status="available",
                current_crew_id=crews[1].id,
                current_project_id=1,
                employment_type="contract",
                hire_date=date(2024, 6, 15),
                daily_cost=720000,
                medical_status_id=medical.id,
                insurance_status="active",
                safety_clearance="cleared",
                productivity_score=72,
                reliability_score=78,
                safety_score=85,
                teamwork_score=80,
                quality_score=76,
            ),
            Worker(
                first_name="Reza",
                last_name="Ahmadi",
                national_id="0012345680",
                phone="09120000003",
                trade_id=trades[1].id,
                current_role="Supervisor",
                skill_level="expert",
                availability_status="assigned",
                current_crew_id=crews[0].id,
                current_project_id=1,
                employment_type="permanent",
                hire_date=date(2023, 1, 10),
                daily_cost=950000,
                medical_status_id=medical.id,
                insurance_status="active",
                safety_clearance="cleared",
                productivity_score=90,
                reliability_score=92,
                safety_score=94,
                teamwork_score=88,
                quality_score=91,
                leadership_score=89,
            ),
        ]
        session.add_all(workers)
        session.flush()

        session.add_all([
            WorkerSkill(
                worker_id=workers[0].id,
                skill_id=skills[0].id,
                proficiency_level="expert",
                experience_years=8,
            ),
            WorkerSkill(
                worker_id=workers[1].id,
                skill_id=skills[2].id,
                proficiency_level="intermediate",
                experience_years=4,
            ),
            WorkerCertification(
                worker_id=workers[0].id,
                certification_id=certs[0].id,
                issue_date=date.today() - timedelta(days=180),
                expiry_date=date.today() + timedelta(days=185),
                status="active",
            ),
            WorkerCertification(
                worker_id=workers[2].id,
                certification_id=certs[1].id,
                issue_date=date.today() - timedelta(days=300),
                expiry_date=date.today() + timedelta(days=65),
                status="active",
            ),
            Attendance(
                worker_id=workers[0].id,
                date=date.today(),
                shift="day",
                check_in="07:00",
                check_out="16:00",
                status="present",
            ),
            Assignment(
                worker_id=workers[0].id,
                work_order_id=1,
                task_id=1,
                crew_id=crews[0].id,
                project_id=1,
                assigned_date=date.today(),
                assigned_by="Operations",
                status="active",
                readiness_status="ready",
            ),
        ])

        session.commit()
        print("Workforce foundation data seeded.")

    finally:
        session.close()


if __name__ == "__main__":
    seed()
