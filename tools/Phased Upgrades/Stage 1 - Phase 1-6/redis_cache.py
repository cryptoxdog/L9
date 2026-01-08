"""
Redis Cache Layer - TTL-based caching for memory operations
"""

import redis.asyncio as redis
import json
import logging
from typing import List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis caching layer with TTL expiration."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        ttl_search_sec: int = 300,
        ttl_governance_sec: int = 3600
    ):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.ttl_search = ttl_search_sec
        self.ttl_governance = ttl_governance_sec
        self.client: Optional[redis.Redis] = None
        self.logger = logger
    
    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            self.client = await redis.from_url(
                f"redis://{self.host}:{self.port}/{self.db}",
                password=self.password,
                decode_responses=True,
                socket_connect_timeout=5
            )
            await self.client.ping()
            self.logger.info(f"Connected to Redis: {self.host}:{self.port}")
        except Exception as e:
            raise Exception(f"Failed to connect to Redis: {e}")
    
    def _make_key(self, prefix: str, *parts) -> str:
        """Build cache key."""
        key_parts = [prefix] + list(parts)
        return ":".join(str(p) for p in key_parts)
    
    async def get_search(
        self,
        query: str,
        segment: str,
        agent_id: str
    ) -> Optional[List]:
        """Retrieve cached search results."""
        if not self.client:
            return None
        
        try:
            key = self._make_key("search", segment, agent_id)
            cached = await self.client.get(key)
            if cached:
                self.logger.debug(f"Cache HIT: {key}")
                return json.loads(cached)
            
            self.logger.debug(f"Cache MISS: {key}")
            return None
        except Exception as e:
            self.logger.warning(f"Cache get failed: {e}")
            return None
    
    async def set_search(
        self,
        query: str,
        segment: str,
        agent_id: str,
        packets: List
    ) -> None:
        """Cache search results."""
        if not self.client:
            return
        
        try:
            key = self._make_key("search", segment, agent_id)
            await self.client.setex(key, self.ttl_search, json.dumps(packets))
            self.logger.debug(f"Cache SET: {key} (TTL {self.ttl_search}s)")
        except Exception as e:
            self.logger.warning(f"Cache set failed: {e}")
    
    async def invalidate_segment(self, segment: str, agent_id: str) -> None:
        """Clear cache for segment/agent combo."""
        if not self.client:
            return
        
        try:
            pattern = f"search:{segment}:{agent_id}"
            cursor = 0
            deleted = 0
            
            while True:
                cursor, keys = await self.client.scan(cursor, match=pattern, count=100)
                if keys:
                    deleted += await self.client.delete(*keys)
                if cursor == 0:
                    break
            
            self.logger.debug(f"Invalidated {deleted} cache keys")
        except Exception as e:
            self.logger.warning(f"Cache invalidation failed: {e}")
    
    async def health_check(self) -> bool:
        """Check Redis is alive."""
        if not self.client:
            return False
        
        try:
            await self.client.ping()
            return True
        except Exception:
            return False
    
    async def close(self) -> None:
        """Close connection."""
        if self.client:
            await self.client.close()
            self.logger.info("Redis connection closed")

# ============================================================================
# L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT
# ============================================================================
__dora_block__ = {
    "component_id": "TOO-OPER-006",
    "component_name": "Redis Cache",
    "module_version": "1.0.0",
    "created_at": "2026-01-08T03:15:14Z",
    "created_by": "L9_DORA_Injector",
    "layer": "operations",
    "domain": "tools",
    "type": "utility",
    "status": "active",
    "governance_level": "medium",
    "compliance_required": True,
    "audit_trail": True,
    "purpose": "Implements RedisCache for redis cache functionality",
    "dependencies": [],
}

# ============================================================================
# END L9 DORA BLOCK
# ============================================================================
