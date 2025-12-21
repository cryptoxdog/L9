"""
L9 Runtime - Redis Client
==========================

Production Redis client for L9 with graceful fallback.

Provides:
- Redis connection management
- Task queue backend
- Rate limiting backend
- Session state storage

Version: 1.0.0
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Try to import Redis
try:
    import redis.asyncio as aioredis
    _has_redis = True
except ImportError:
    _has_redis = False
    logger.warning("Redis not available - install with: pip install redis>=5.0.0")


class RedisClient:
    """
    Production Redis client with connection pooling.
    
    Gracefully falls back to None if Redis is unavailable.
    """
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        db: int = 0,
        password: Optional[str] = None,
        decode_responses: bool = True,
    ):
        """
        Initialize Redis client.
        
        Args:
            host: Redis host (default: REDIS_HOST env or 'localhost')
            port: Redis port (default: REDIS_PORT env or 6379)
            db: Redis database number (default: 0)
            password: Redis password (optional)
            decode_responses: Decode responses as strings (default: True)
        """
        if not _has_redis:
            self._client = None
            self._available = False
            logger.warning("Redis not available - operations will fail gracefully")
            return
        
        self._host = host or os.getenv("REDIS_HOST", "localhost")
        self._port = port or int(os.getenv("REDIS_PORT", "6379"))
        self._db = db
        self._password = password or os.getenv("REDIS_PASSWORD")
        self._decode_responses = decode_responses
        self._client: Optional[aioredis.Redis] = None
        self._available = False
    
    async def connect(self) -> bool:
        """
        Connect to Redis server.
        
        Returns:
            True if connected, False if unavailable
        """
        if not _has_redis:
            return False
        
        if self._client is not None:
            return self._available
        
        try:
            self._client = aioredis.Redis(
                host=self._host,
                port=self._port,
                db=self._db,
                password=self._password,
                decode_responses=self._decode_responses,
                socket_connect_timeout=2,
                socket_timeout=2,
                retry_on_timeout=True,
            )
            
            # Test connection
            await self._client.ping()
            self._available = True
            logger.info(f"Redis connected: {self._host}:{self._port}/{self._db}")
            return True
        except Exception as e:
            logger.warning(f"Redis connection failed: {e} - falling back to in-memory")
            self._client = None
            self._available = False
            return False
    
    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._client:
            try:
                await self._client.close()
                logger.info("Redis disconnected")
            except Exception as e:
                logger.warning(f"Error disconnecting Redis: {e}")
            finally:
                self._client = None
                self._available = False
    
    def is_available(self) -> bool:
        """Check if Redis is available."""
        return self._available and self._client is not None
    
    # =========================================================================
    # Task Queue Operations
    # =========================================================================
    
    async def enqueue_task(
        self,
        queue_name: str,
        task_data: dict[str, Any],
        priority: int = 5,
    ) -> Optional[str]:
        """
        Enqueue a task in Redis sorted set (priority queue).
        
        Args:
            queue_name: Queue name (e.g., "l9:tasks")
            task_data: Task data dict
            priority: Priority (lower = higher priority)
            
        Returns:
            Task ID or None if Redis unavailable
        """
        if not self.is_available():
            return None
        
        try:
            import uuid
            task_id = str(uuid.uuid4())
            task_data["task_id"] = task_id
            task_data["priority"] = priority
            
            # Store task data
            task_key = f"{queue_name}:task:{task_id}"
            await self._client.setex(
                task_key,
                3600,  # 1 hour TTL
                json.dumps(task_data),
            )
            
            # Add to priority queue (sorted set)
            await self._client.zadd(
                f"{queue_name}:queue",
                {task_id: priority},
            )
            
            logger.debug(f"Enqueued task {task_id} to {queue_name} with priority {priority}")
            return task_id
        except Exception as e:
            logger.error(f"Redis enqueue failed: {e}")
            return None
    
    async def dequeue_task(self, queue_name: str) -> Optional[dict[str, Any]]:
        """
        Dequeue highest priority task from Redis.
        
        Args:
            queue_name: Queue name
            
        Returns:
            Task data dict or None if queue empty or Redis unavailable
        """
        if not self.is_available():
            return None
        
        try:
            # Get highest priority task (lowest score)
            result = await self._client.zpopmin(f"{queue_name}:queue", count=1)
            
            if not result:
                return None
            
            task_id, _ = result[0]
            task_key = f"{queue_name}:task:{task_id}"
            
            # Get task data
            task_data_str = await self._client.get(task_key)
            if not task_data_str:
                return None
            
            # Delete task data
            await self._client.delete(task_key)
            
            task_data = json.loads(task_data_str)
            logger.debug(f"Dequeued task {task_id} from {queue_name}")
            return task_data
        except Exception as e:
            logger.error(f"Redis dequeue failed: {e}")
            return None
    
    async def queue_size(self, queue_name: str) -> int:
        """Get queue size."""
        if not self.is_available():
            return 0
        
        try:
            return await self._client.zcard(f"{queue_name}:queue")
        except Exception as e:
            logger.error(f"Redis queue_size failed: {e}")
            return 0
    
    # =========================================================================
    # Rate Limiting Operations
    # =========================================================================
    
    async def get_rate_limit(self, key: str) -> int:
        """
        Get current rate limit count.
        
        Args:
            key: Rate limit key (e.g., "rate_limit:google:now")
            
        Returns:
            Current count or 0 if unavailable
        """
        if not self.is_available():
            return 0
        
        try:
            value = await self._client.get(key)
            return int(value) if value else 0
        except Exception as e:
            logger.error(f"Redis get_rate_limit failed: {e}")
            return 0
    
    async def set_rate_limit(self, key: str, value: int, ttl: int = 60) -> bool:
        """
        Set rate limit count with TTL.
        
        Args:
            key: Rate limit key
            value: Count value
            ttl: Time to live in seconds (default: 60)
            
        Returns:
            True if set, False if unavailable
        """
        if not self.is_available():
            return False
        
        try:
            await self._client.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.error(f"Redis set_rate_limit failed: {e}")
            return False
    
    async def increment_rate_limit(self, key: str, ttl: int = 60) -> int:
        """
        Increment rate limit counter.
        
        Args:
            key: Rate limit key
            ttl: Time to live in seconds (default: 60)
            
        Returns:
            New count or 0 if unavailable
        """
        if not self.is_available():
            return 0
        
        try:
            count = await self._client.incr(key)
            if count == 1:  # First increment, set TTL
                await self._client.expire(key, ttl)
            return count
        except Exception as e:
            logger.error(f"Redis increment_rate_limit failed: {e}")
            return 0
    
    async def decrement_rate_limit(self, key: str) -> int:
        """Decrement rate limit counter."""
        if not self.is_available():
            return 0
        
        try:
            return await self._client.decr(key)
        except Exception as e:
            logger.error(f"Redis decrement_rate_limit failed: {e}")
            return 0
    
    # =========================================================================
    # Generic Key-Value Operations
    # =========================================================================
    
    async def get(self, key: str) -> Optional[str]:
        """Get value by key."""
        if not self.is_available():
            return None
        
        try:
            return await self._client.get(key)
        except Exception as e:
            logger.error(f"Redis get failed: {e}")
            return None
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Set key-value with optional TTL."""
        if not self.is_available():
            return False
        
        try:
            if ttl:
                await self._client.setex(key, ttl, value)
            else:
                await self._client.set(key, value)
            return True
        except Exception as e:
            logger.error(f"Redis set failed: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key."""
        if not self.is_available():
            return False
        
        try:
            await self._client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis delete failed: {e}")
            return False
    
    async def keys(self, pattern: str) -> list[str]:
        """Get keys matching pattern."""
        if not self.is_available():
            return []
        
        try:
            return [key async for key in self._client.scan_iter(match=pattern)]
        except Exception as e:
            logger.error(f"Redis keys failed: {e}")
            return []


# =============================================================================
# Singleton Factory
# =============================================================================

_redis_client: Optional[RedisClient] = None


async def get_redis_client() -> Optional[RedisClient]:
    """
    Get or create singleton Redis client.
    
    Returns:
        RedisClient instance or None if unavailable
    """
    global _redis_client
    
    if _redis_client is None:
        _redis_client = RedisClient()
        await _redis_client.connect()
    
    return _redis_client if _redis_client.is_available() else None


async def close_redis_client() -> None:
    """Close singleton Redis client."""
    global _redis_client
    if _redis_client:
        await _redis_client.disconnect()
        _redis_client = None


__all__ = ["RedisClient", "get_redis_client", "close_redis_client"]

