"""Phase 1 FastAPI routers."""

from backend.phase1.routers.analytics_router import router as analytics_router
from backend.phase1.routers.pilot_router import router as pilot_router
from backend.phase1.routers.planning_router import router as planning_router
from backend.phase1.routers.runtime_router import router as runtime_router

__all__ = [
    "analytics_router",
    "pilot_router",
    "planning_router",
    "runtime_router",
]
