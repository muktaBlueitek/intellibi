from fastapi import FastAPI

from app.core.config import settings
from app.api.v1.endpoints import health, auth, users, datasources, dashboards, widgets, upload


def create_application() -> FastAPI:
    app = FastAPI(
        title="IntelliBI Backend",
        version="0.1.0",
        description="Backend API for the IntelliBI Business Intelligence Platform.",
    )

    # Routers
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
    app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
    app.include_router(datasources.router, prefix="/api/v1/datasources", tags=["datasources"])
    app.include_router(dashboards.router, prefix="/api/v1/dashboards", tags=["dashboards"])
    app.include_router(widgets.router, prefix="/api/v1/widgets", tags=["widgets"])
    app.include_router(upload.router, prefix="/api/v1/upload", tags=["upload"])

    return app


app = create_application()


@app.get("/")
def read_root():
    return {
        "app": "IntelliBI Backend",
        "environment": settings.ENVIRONMENT,
        "message": "Welcome to IntelliBI backend.",
    }



