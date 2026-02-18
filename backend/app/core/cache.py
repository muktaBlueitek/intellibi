import json
import hashlib
from typing import Optional, Any, Callable
from functools import wraps
import redis
from redis.exceptions import ConnectionError, TimeoutError

from app.core.config import settings


class CacheService:
    """Redis-based cache service for API responses and data caching."""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self._connect()

    def _connect(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            # Test connection
            self.redis_client.ping()
        except (ConnectionError, TimeoutError, Exception) as e:
            # If Redis is not available, cache operations will be no-ops
            self.redis_client = None
            print(f"Warning: Redis connection failed: {e}. Caching disabled.")

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.redis_client:
            return None
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            print(f"Cache get error: {e}")
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL."""
        if not self.redis_client:
            return False
        try:
            ttl = ttl or settings.CACHE_TTL
            serialized = json.dumps(value, default=str)
            return self.redis_client.setex(key, ttl, serialized)
        except Exception as e:
            print(f"Cache set error: {e}")
        return False

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.redis_client:
            return False
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            print(f"Cache delete error: {e}")
        return False

    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        if not self.redis_client:
            return 0
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
        except Exception as e:
            print(f"Cache delete_pattern error: {e}")
        return 0

    def invalidate_user_cache(self, user_id: int):
        """Invalidate all cache entries for a specific user."""
        patterns = [
            f"user:{user_id}:*",
            f"dashboard:*:user:{user_id}",
            f"datasource:*:user:{user_id}",
        ]
        for pattern in patterns:
            self.delete_pattern(pattern)

    def invalidate_dashboard_cache(self, dashboard_id: int):
        """Invalidate cache for a specific dashboard."""
        patterns = [
            f"dashboard:{dashboard_id}:*",
            f"widget:*:dashboard:{dashboard_id}",
        ]
        for pattern in patterns:
            self.delete_pattern(pattern)


# Global cache instance
cache_service = CacheService()


def cache_key_generator(*args, **kwargs) -> str:
    """Generate cache key from function arguments."""
    # Create a hash from args and kwargs
    key_parts = []
    for arg in args:
        if hasattr(arg, 'id'):
            key_parts.append(f"{type(arg).__name__}:{arg.id}")
        elif isinstance(arg, (int, str)):
            key_parts.append(str(arg))
    
    for k, v in sorted(kwargs.items()):
        if isinstance(v, (int, str, bool)):
            key_parts.append(f"{k}:{v}")
        elif hasattr(v, 'id'):
            key_parts.append(f"{k}:{type(v).__name__}:{v.id}")
    
    key_string = ":".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """
    Decorator to cache function results.
    
    Usage:
        @cached(ttl=300, key_prefix="dashboard")
        def get_dashboard(dashboard_id: int):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            func_name = func.__name__
            key_suffix = cache_key_generator(*args, **kwargs)
            cache_key = f"{key_prefix}:{func_name}:{key_suffix}" if key_prefix else f"{func_name}:{key_suffix}"
            
            # Try to get from cache
            cached_value = cache_service.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function (handle both sync and async)
            import inspect
            if inspect.iscoroutinefunction(func):
                # For async functions, return a coroutine that caches the result
                async def async_wrapper():
                    result = await func(*args, **kwargs)
                    cache_service.set(cache_key, result, ttl)
                    return result
                return async_wrapper()
            else:
                # Sync function
                result = func(*args, **kwargs)
                cache_service.set(cache_key, result, ttl)
                return result
        
        return wrapper
    return decorator
