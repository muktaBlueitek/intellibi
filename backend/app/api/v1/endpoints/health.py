from fastapi import APIRouter, Request

from app.core.config import settings
from app.core.rate_limit import limiter


router = APIRouter()


@router.get("/health", summary="Health check")
@limiter.exempt
def health_check(request: Request):
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }



