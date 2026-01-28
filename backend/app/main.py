from fastapi import FastAPI

from app.core.config import settings
from app.api.v1.endpoints import health


def create_application() -> FastAPI:
    app = FastAPI(
        title="IntelliBI Backend",
        version="0.1.0",
        description="Backend API for the IntelliBI Business Intelligence Platform.",
    )

    # Routers
    app.include_router(health.router, prefix="/api/v1", tags=["health"])

    return app


app = create_application()


@app.get("/")
def read_root():
    return {
        "app": "IntelliBI Backend",
        "environment": settings.ENVIRONMENT,
        "message": "Welcome to IntelliBI backend.",
    }


