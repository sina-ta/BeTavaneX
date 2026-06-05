"""Phase 1 FastAPI routers."""

from backend.phase1.routers.analytics_router import router as analytics_router
from backend.phase1.routers.dependency_router import router as dependency_router
from backend.phase1.routers.pilot_router import router as pilot_router
from backend.phase1.routers.planning_router import router as planning_router
from backend.phase1.routers.readiness_router import router as readiness_router
from backend.phase1.routers.runtime_router import router as runtime_router

__all__ = [
    "analytics_router",
    "dependency_router",
    "pilot_router",
    "planning_router",
    "readiness_router",
    "runtime_router",
]
