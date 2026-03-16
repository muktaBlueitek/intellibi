"""
API Rate limiting using SlowAPI.
Applies configurable limits to protect the API from abuse.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings


def get_identifier(request):
    """Use client IP for rate limit key. Can be extended to use user ID when authenticated."""
    return get_remote_address(request)


# Default limits; can be overridden via application_limits when adding middleware
_default_limit = settings.RATE_LIMIT_GENERAL if settings.RATE_LIMIT_ENABLED else "10000/minute"

limiter = Limiter(
    key_func=get_identifier,
    default_limits=[_default_limit],
    storage_uri="memory://",  # Use Redis in production: f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
)
