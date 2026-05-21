from backend.database import SessionLocal

from backend.models.hr_models import (
    Role,
    Crew,
    Worker
)

from datetime import date


session = SessionLocal()

# =========================
# Roles
# =========================

engineer_role = Role(
    title="Engineer"
)

worker_role = Role(
    title="Worker"
)

foreman_role = Role(
    title="Foreman"
)

session.add_all([
    engineer_role,
    worker_role,
    foreman_role
])

session.commit()

# =========================
# Crews
# =========================

structural_crew = Crew(
    name="Structural Team",
    description="Concrete + Rebar"
)

mep_crew = Crew(
    name="MEP Team",
    description="Mechanical + Electrical"
)

session.add_all([
    structural_crew,
    mep_crew
])

session.commit()

# =========================
# Workers
# =========================

workers = [

    Worker(
        full_name="Sina Tafaroju",
        phone="09120000001",
        national_id="1234567890",
        role_id=engineer_role.id,
        crew_id=structural_crew.id,
        join_date=date.today(),
        status="Active",
        daily_wage=4500000,
        score=92
    ),

    Worker(
        full_name="Ali Moradi",
        phone="09120000002",
        national_id="2234567890",
        role_id=worker_role.id,
        crew_id=structural_crew.id,
        join_date=date.today(),
        status="Active",
        daily_wage=2800000,
        score=81
    ),

    Worker(
        full_name="Reza Ahmadi",
        phone="09120000003",
        national_id="3234567890",
        role_id=foreman_role.id,
        crew_id=mep_crew.id,
        join_date=date.today(),
        status="Active",
        daily_wage=3500000,
        score=88
    )
]

session.add_all(workers)

session.commit()

print("✅ HR Seed Data Inserted")