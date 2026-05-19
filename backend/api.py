from fastapi import FastAPI

from backend.database import engine

from backend.models import Base

from fastapi.middleware.cors import CORSMiddleware

from backend.routers.dashboard_router import router as dashboard_router
from backend.routers.work_order_router import router as work_order_router
from backend.routers.report_router import router as report_router


app = FastAPI()

Base.metadata.create_all(bind=engine)

# ✅ CORS
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