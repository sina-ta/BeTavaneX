from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from backend.database import engine
from backend.extensions.registry import (
    include_enabled_extension_routers,
    register_enabled_extension_models,
)
from backend.models.main_models import Base

import backend.validation.models  # noqa: F401
import backend.lifecycle.models  # noqa: F401

from backend.routers.dashboard_router import (
    router as dashboard_router,
)

from backend.routers.work_order_router import (
    router as work_order_router,
)

from backend.routers.report_router import (
    router as report_router,
)

from backend.routers.task_detail_router import (
    router as task_detail_router,
)

from backend.routers.analytics_router import (
    router as analytics_router,
)

from backend.validation.routers.validation_router import (
    router as validation_router,
)

from backend.lifecycle.routers.lifecycle_router import (
    router as lifecycle_router,
)

app = FastAPI()

register_enabled_extension_models()
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard_router)
app.include_router(work_order_router)
app.include_router(report_router)
app.include_router(task_detail_router)
app.include_router(analytics_router)
app.include_router(validation_router)
app.include_router(lifecycle_router)
include_enabled_extension_routers(app)
