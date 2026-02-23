from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.api.v1.endpoints import health, auth, users, datasources, dashboards, widgets, upload, database_connections, analytics, chatbot, websocket, notifications


def create_application() -> FastAPI:
    app = FastAPI(
        title="IntelliBI API",
        version="0.1.0",
        description="""
## IntelliBI - Intelligent Business Intelligence Platform

REST API for dashboards, data sources, analytics, and AI-powered chatbot.

### Features
- **Authentication** - JWT-based auth, user management
- **Dashboards** - Create, share, version dashboards with widgets
- **Data Sources** - CSV/Excel upload, PostgreSQL/MySQL connectors
- **Analytics** - Query processing, aggregations, time-series
- **Chatbot** - Natural language to SQL, insights, visualization suggestions
- **Real-time** - WebSocket for live updates and notifications
        """.strip(),
        docs_url="/api/v1/docs",
        redoc_url="/api/v1/redoc",
        openapi_url="/api/v1/openapi.json",
        openapi_tags=[
            {"name": "health", "description": "Health check endpoints"},
            {"name": "authentication", "description": "Login, register, JWT"},
            {"name": "users", "description": "User management"},
            {"name": "datasources", "description": "Data source CRUD and upload"},
            {"name": "dashboards", "description": "Dashboard CRUD, layout, sharing"},
            {"name": "widgets", "description": "Dashboard widget management"},
            {"name": "analytics", "description": "Query execution, aggregations"},
            {"name": "chatbot", "description": "AI chatbot, conversations"},
            {"name": "websocket", "description": "Real-time WebSocket"},
            {"name": "notifications", "description": "User notifications"},
        ],
        contact={"name": "IntelliBI", "url": "https://github.com/muktaBlueitek/intellibi"},
        license_info={"name": "MIT"},
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URL
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
    app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
    app.include_router(datasources.router, prefix="/api/v1/datasources", tags=["datasources"])
    app.include_router(dashboards.router, prefix="/api/v1/dashboards", tags=["dashboards"])
    app.include_router(widgets.router, prefix="/api/v1/widgets", tags=["widgets"])
    app.include_router(upload.router, prefix="/api/v1/upload", tags=["upload"])
    app.include_router(database_connections.router, prefix="/api/v1/database", tags=["database-connections"])
    app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
    app.include_router(chatbot.router, prefix="/api/v1/chatbot", tags=["chatbot"])
    app.include_router(websocket.router, prefix="/api/v1", tags=["websocket"])
    app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])

    # Global exception handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Validation error",
                "errors": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        if settings.ENVIRONMENT == "development":
            raise exc
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected error occurred. Please try again later.",
            },
        )

    return app


app = create_application()


@app.get("/")
def read_root():
    return {
        "app": "IntelliBI Backend",
        "environment": settings.ENVIRONMENT,
        "message": "Welcome to IntelliBI backend.",
    }



