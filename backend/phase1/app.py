"""Phase 1 FastAPI application bootstrap.

Composition root for the Architecture Freeze v1 backend. It only wires the
verified planning and runtime routers (mounted at /planning and /runtime). It
does not touch the legacy ``backend/api.py`` application.
"""

from __future__ import annotations

from fastapi import FastAPI

from backend.phase1.routers import planning_router, runtime_router


def create_app() -> FastAPI:
    app = FastAPI(title="BetavanX Phase 1", version="1.0.0")
    app.include_router(planning_router)
    app.include_router(runtime_router)
    return app


app = create_app()
