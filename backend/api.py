from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from backend.database import engine

from backend.models.main_models import Base

# =========================
# Routers
# =========================

from backend.routers.dashboard_router import (
    router as dashboard_router
)

from backend.routers.work_order_router import (
    router as work_order_router
)

from backend.routers.report_router import (
    router as report_router
)

from backend.routers.task_detail_router import (
    router as task_detail_router
)

from backend.routers.hr_router import (
    router as hr_router
)

# =========================
# HR Models
# =========================

from backend.models.hr_models import (
    Role,
    Crew,
    Worker,
    Skill,
    WorkerSkill,
    WorkerAttendance,
    WorkerPayment,
    WorkerScore,
    TaskAssignment,
    WorkerTraining,
    WorkerCertificate,
    WorkerEquipment
)

# =========================
# Create App
# =========================

app = FastAPI()

# =========================
# Database
# =========================

Base.metadata.create_all(bind=engine)

# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Register Routers
# =========================

app.include_router(dashboard_router)

app.include_router(work_order_router)

app.include_router(report_router)

app.include_router(task_detail_router)

app.include_router(hr_router)