from fastapi import FastAPI

from backend.workforce.routers.workforce_router import (
    router as workforce_router,
)


def include_router(app: FastAPI) -> None:
    app.include_router(workforce_router)
