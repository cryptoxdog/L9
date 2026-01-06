"""
PostgreSQL Backend with pgvector
=================================

Implements SubstrateService over asyncpg + pgvector for semantic search.
Production-grade: connection pooling, schema management, vector indexes.
"""

import asyncpg
import json
import logging
from typing import List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PostgresBackend:
    """PostgreSQL backend with pgvector for memory storage."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        user: str = "postgres",
        password: str = "postgres",
        database: str = "l9_memory",
        min_pool_size: int = 5,
        max_pool_size: int = 20,
        query_timeout: float = 30.0
    ):
        self.config = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
            "min_size": min_pool_size,
            "max_size": max_pool_size,
            "command_timeout": query_timeout
        }
        self.pool: Optional[asyncpg.Pool] = None
        self.logger = logger
    
    async def connect(self) -> None:
        """Initialize connection pool and create schema."""
        try:
            self.pool = await asyncpg.create_pool(**self.config)
            self.logger.info(f"Connected to Postgres: {self.config['host']}:{self.config['port']}")
            
            # Create schema
            await self._create_schema()
            self.logger.info("Memory schema initialized")
        
        except asyncpg.PostgresError as e:
            raise Exception(f"Failed to connect to Postgres: {e}")
    
    async def _create_schema(self) -> None:
        """Create tables and indexes for memory storage."""
        async with self.pool.acquire() as conn:
            # Enable pgvector extension
            try:
                await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            except asyncpg.PostgresError:
                self.logger.warning("pgvector extension may not be available")
            
            # Create memory_packets table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_packets (
                    chunk_id VARCHAR(255) PRIMARY KEY,
                    segment VARCHAR(50) NOT NULL,
                    agent_id VARCHAR(255) NOT NULL,
                    content JSONB NOT NULL,
                    metadata JSONB DEFAULT '{}',
                    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    embedding vector(1536),
                    version INT DEFAULT 1,
                    expires_at TIMESTAMPTZ,
                    
                    CONSTRAINT chunk_id_unique UNIQUE (chunk_id),
                    CONSTRAINT expires_at_check CHECK (expires_at IS NULL OR expires_at > timestamp)
                )
            """)
            
            # Create indexes for fast queries
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_segment_agent
                ON memory_packets (segment, agent_id, timestamp DESC)
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_expires
                ON memory_packets (expires_at)
                WHERE expires_at IS NOT NULL
            """)
            
            # Vector index for semantic search (HNSW preferred)
            try:
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_memory_embedding
                    ON memory_packets USING hnsw (embedding vector_cosine_ops)
                    WITH (m=16, ef_construction=200)
                """)
            except asyncpg.PostgresError:
                self.logger.warning("HNSW not available, using IVFFLAT")
                try:
                    await conn.execute("""
                        CREATE INDEX IF NOT EXISTS idx_memory_embedding
                        ON memory_packets USING ivfflat (embedding vector_cosine_ops)
                        WITH (lists=100)
                    """)
                except asyncpg.PostgresError as e:
                    self.logger.warning(f"Vector index creation failed: {e}")
    
    async def write_packet(self, packet) -> str:
        """Write packet to Postgres with upsert."""
        if not self.pool:
            raise Exception("Not connected to Postgres")
        
        try:
            chunk_id, segment, agent_id, content, metadata, timestamp, embedding, version, expires_at = packet.as_postgres_tuple()
            
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO memory_packets (
                        chunk_id, segment, agent_id, content, metadata,
                        timestamp, embedding, version, expires_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    ON CONFLICT (chunk_id) DO UPDATE SET
                        content = EXCLUDED.content,
                        metadata = EXCLUDED.metadata,
                        embedding = EXCLUDED.embedding,
                        version = EXCLUDED.version + 1,
                        expires_at = EXCLUDED.expires_at
                """, chunk_id, segment, agent_id, content, metadata, timestamp, embedding, version, expires_at)
            
            self.logger.debug(f"Wrote packet {chunk_id} to Postgres")
            return chunk_id
        
        except asyncpg.PostgresError as e:
            raise Exception(f"Failed to write packet: {e}")
    
    async def search_packets(
        self,
        query: str,
        segment: str,
        agent_id: str,
        limit: int = 10
    ) -> List:
        """Keyword search in JSONB content."""
        if not self.pool:
            raise Exception("Not connected to Postgres")
        
        if limit > 50:
            limit = 50
        
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM memory_packets
                    WHERE segment = $1
                        AND agent_id = $2
                        AND (content::text ILIKE $3 OR metadata::text ILIKE $3)
                        AND (expires_at IS NULL OR expires_at > NOW())
                    ORDER BY timestamp DESC
                    LIMIT $4
                """, segment, agent_id, f"%{query}%", limit)
                
                # Returns list of asyncpg.Record objects
                return rows
        
        except asyncpg.PostgresError as e:
            raise Exception(f"Search failed: {e}")
    
    async def semantic_search(
        self,
        embedding: List[float],
        segment: str,
        agent_id: str,
        limit: int = 10
    ) -> List:
        """Vector similarity search via pgvector."""
        if not self.pool:
            raise Exception("Not connected to Postgres")
        
        if not embedding or len(embedding) != 1536:
            raise Exception("Invalid embedding: must be 1536-dimensional")
        
        if limit > 50:
            limit = 50
        
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT
                        *,
                        1 - (embedding <-> $1::vector) as similarity
                    FROM memory_packets
                    WHERE segment = $2
                        AND agent_id = $3
                        AND embedding IS NOT NULL
                        AND (expires_at IS NULL OR expires_at > NOW())
                    ORDER BY embedding <-> $1::vector
                    LIMIT $4
                """, embedding, segment, agent_id, limit)
                
                return rows
        
        except asyncpg.PostgresError as e:
            raise Exception(f"Semantic search failed: {e}")
    
    async def delete_expired(self) -> int:
        """Delete packets past expires_at timestamp."""
        if not self.pool:
            raise Exception("Not connected to Postgres")
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM memory_packets
                    WHERE expires_at IS NOT NULL AND expires_at < NOW()
                """)
                
                # Parse "DELETE N" string result
                count = int(result.split()[-1]) if result else 0
                
                if count > 0:
                    self.logger.info(f"Deleted {count} expired packets")
                
                return count
        
        except asyncpg.PostgresError as e:
            raise Exception(f"Delete expired failed: {e}")
    
    async def health_check(self) -> bool:
        """Verify Postgres connection is healthy."""
        if not self.pool:
            raise Exception("Not connected")
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchval("SELECT 1")
                return result == 1
        except asyncpg.PostgresError as e:
            raise Exception(f"Health check failed: {e}")
    
    async def close(self) -> None:
        """Close connection pool."""
        if self.pool:
            await self.pool.close()
            self.logger.info("Postgres connection closed")
