"""Unit tests for app.core.cache."""
import pytest
from unittest.mock import patch, MagicMock

from app.core.cache import CacheService, cache_key_generator


class TestCacheKeyGenerator:
    def test_deterministic_for_same_args(self):
        key1 = cache_key_generator(1, 2)
        key2 = cache_key_generator(1, 2)
        assert key1 == key2

    def test_different_for_different_args(self):
        key1 = cache_key_generator(1, 2)
        key2 = cache_key_generator(1, 3)
        assert key1 != key2


class TestCacheService:
    def test_get_returns_none_when_redis_unavailable(self):
        """When Redis client is None (connection failed), get returns None."""
        service = CacheService()
        if service.redis_client is None:
            assert service.get("any_key") is None
        else:
            # If Redis is available, get for non-existent key returns None
            assert service.get("nonexistent_key_xyz_123") is None

    def test_set_returns_false_when_redis_unavailable(self):
        """When Redis client is None, set returns False."""
        service = CacheService()
        if service.redis_client is None:
            assert service.set("key", "value") is False
