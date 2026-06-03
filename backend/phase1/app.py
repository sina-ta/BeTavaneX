"""Phase 1 FastAPI application bootstrap.



Composition root for the Architecture Freeze v1 backend. It wires the verified

planning and runtime routers (mounted at /planning and /runtime) behind

authentication, plus the OAuth2 token endpoint at /auth/token. It does not touch

the legacy ``backend/api.py`` application.

"""



from __future__ import annotations



from contextlib import asynccontextmanager



from fastapi import Depends, FastAPI, Response

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError



from backend.config import get_settings

from backend.db.session import engine

from backend.observability import (

    RequestObservabilityMiddleware,

    configure_logging,

)

from backend.phase1.auth.auth import auth_router

from backend.phase1.auth.dependencies import get_current_active_user

from backend.phase1.routers import (
    analytics_router,
    pilot_router,
    planning_router,
    runtime_router,
)



_DESCRIPTION = """

BetavanX Phase 1 operational API (Architecture Freeze v1).



* **Planning** — create projects, WBS items, locations, activity instances,

  workflow steps, and work orders.

* **Runtime** — assign work orders, submit daily reports, approve workflow

  steps, and read project / activity-instance dashboards.



All `/planning` and `/runtime` endpoints require a Bearer token obtained from

`POST /auth/token` (OAuth2 password flow).

"""



_OPENAPI_TAGS = [

    {"name": "auth", "description": "Obtain and manage access tokens."},

    {"name": "planning", "description": "Planning-layer creation use cases."},

    {"name": "runtime", "description": "Runtime execution and dashboard use cases."},

]





@asynccontextmanager

async def _lifespan(_app: FastAPI):

    from backend.phase1.startup import validate_startup



    validate_startup()

    yield





def create_app() -> FastAPI:

    settings = get_settings()

    configure_logging(level=settings.log_level, json_logs=settings.log_json)



    app = FastAPI(

        title="BetavanX Phase 1 API",

        version="1.0.0",

        description=_DESCRIPTION,

        openapi_tags=_OPENAPI_TAGS,

        contact={"name": "BetavanX Backend"},

        lifespan=_lifespan,

    )



    app.add_middleware(RequestObservabilityMiddleware)

    app.add_middleware(

        CORSMiddleware,

        allow_origins=list(settings.cors_origins),

        allow_credentials=True,

        allow_methods=["*"],

        allow_headers=["*"],

    )



    @app.get("/health/live", tags=["ops"])
    def liveness_check() -> dict[str, str]:
        return {
            "status": "ok",
            "app_env": settings.app_env,
        }

    @app.get("/health", tags=["ops"])
    def readiness_check() -> Response:
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except SQLAlchemyError:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "degraded",
                    "database": "unavailable",
                    "app_env": settings.app_env,
                },
            )
        return JSONResponse(
            content={
                "status": "ok",
                "database": "connected",
                "app_env": settings.app_env,
            },
        )



    # Public: token issuance for the OAuth2 password flow.

    app.include_router(auth_router)



    # Secured: every planning/runtime endpoint requires an active authenticated

    # user. Applied at router level so endpoint code stays unchanged.

    app.include_router(

        planning_router,

        dependencies=[Depends(get_current_active_user)],

    )

    app.include_router(

        runtime_router,

        dependencies=[Depends(get_current_active_user)],

    )

    app.include_router(

        pilot_router,

        dependencies=[Depends(get_current_active_user)],

    )

    app.include_router(

        analytics_router,

        dependencies=[Depends(get_current_active_user)],

    )

    return app





app = create_app()

