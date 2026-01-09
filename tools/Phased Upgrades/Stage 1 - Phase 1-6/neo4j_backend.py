"""
Neo4j Knowledge Graph Backend
=============================

Implements memory operations over Neo4j for graph relationships.
Tracks tool calls, agent decisions, knowledge relationships.
"""

import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class Neo4jBackend:
    """
    Neo4j backend for memory graph.
    
    Nodes:
    - MemoryChunk: Memory packets
    - Agent: Agent instances
    - Tool: Tool definitions
    
    Relationships:
    - HAS_CHUNK: Agent owns memory chunks
    - USES_TOOL: Agent uses tool
    """
    
    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "password",
        database: str = "neo4j"
    ):
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database
        self.driver = None
        self.logger = logger
    
    async def connect(self) -> None:
        """Initialize Neo4j connection."""
        try:
            # Import here to avoid hard dependency
            from neo4j import AsyncGraphDatabase, basic_auth
            
            self.driver = AsyncGraphDatabase.driver(
                self.uri,
                auth=basic_auth(self.user, self.password),
                connection_timeout=30,
                max_pool_size=50
            )
            
            # Verify connection
            async with self.driver.session(database=self.database) as session:
                await session.run("RETURN 1")
            
            self.logger.info(f"Connected to Neo4j: {self.uri}")
            
            # Create indexes
            await self._create_indexes()
        
        except Exception as e:
            raise Exception(f"Failed to connect to Neo4j: {e}")
    
    async def _create_indexes(self) -> None:
        """Create query indexes."""
        if not self.driver:
            return
        
        async with self.driver.session(database=self.database) as session:
            try:
                await session.run(
                    "CREATE INDEX memory_chunk_id IF NOT EXISTS FOR (n:MemoryChunk) ON (n.chunk_id)"
                )
                await session.run(
                    "CREATE INDEX agent_id IF NOT EXISTS FOR (n:Agent) ON (n.agent_id)"
                )
                self.logger.info("Neo4j indexes created")
            except Exception as e:
                self.logger.warning(f"Index creation: {e}")
    
    async def write_packet(self, packet) -> str:
        """Write packet as graph node."""
        if not self.driver:
            raise Exception("Not connected to Neo4j")
        
        try:
            async with self.driver.session(database=self.database) as session:
                chunk_id = packet.get("chunk_id") if isinstance(packet, dict) else packet.chunk_id
                agent_id = packet.get("agent_id") if isinstance(packet, dict) else packet.agent_id
                
                await session.run("""
                    MERGE (chunk:MemoryChunk {chunk_id: $chunk_id})
                    SET chunk.agent_id = $agent_id
                    WITH chunk
                    MATCH (a:Agent {agent_id: $agent_id})
                    MERGE (a)-[:HAS_CHUNK]->(chunk)
                """, chunk_id=chunk_id, agent_id=agent_id)
            
            self.logger.debug(f"Wrote chunk {chunk_id} to Neo4j")
            return chunk_id
        
        except Exception as e:
            raise Exception(f"Neo4j write failed: {e}")
    
    async def search_packets(
        self,
        query: str,
        segment: str,
        agent_id: str,
        limit: int = 10
    ) -> List:
        """Search memory chunks in graph."""
        if not self.driver:
            raise Exception("Not connected to Neo4j")
        
        try:
            async with self.driver.session(database=self.database) as session:
                result = await session.run("""
                    MATCH (chunk:MemoryChunk)
                    WHERE chunk.segment = $segment
                        AND chunk.agent_id = $agent_id
                    RETURN chunk
                    ORDER BY chunk.timestamp DESC
                    LIMIT $limit
                """, segment=segment, agent_id=agent_id, limit=min(limit, 50))
                
                records = await result.data()
                return records if records else []
        
        except Exception as e:
            raise Exception(f"Neo4j search failed: {e}")
    
    async def semantic_search(
        self,
        embedding: List[float],
        segment: str,
        agent_id: str,
        limit: int = 10
    ) -> List:
        """Neo4j doesn't support vector search; return empty."""
        return []
    
    async def delete_expired(self) -> int:
        """Delete expired chunks from graph."""
        if not self.driver:
            raise Exception("Not connected to Neo4j")
        
        try:
            async with self.driver.session(database=self.database) as session:
                result = await session.run("""
                    MATCH (chunk:MemoryChunk)
                    WHERE chunk.expires_at IS NOT NULL AND chunk.expires_at < timestamp()
                    DETACH DELETE chunk
                    RETURN COUNT(*) as count
                """)
                
                record = await result.single()
                count = record["count"] if record else 0
                return count
        
        except Exception as e:
            raise Exception(f"Neo4j delete failed: {e}")
    
    async def health_check(self) -> bool:
        """Verify Neo4j is responsive."""
        if not self.driver:
            raise Exception("Not connected")
        
        try:
            async with self.driver.session(database=self.database) as session:
                result = await session.run("RETURN 1")
                return True
        except Exception as e:
            raise Exception(f"Neo4j health check failed: {e}")
    
    async def close(self) -> None:
        """Close connection."""
        if self.driver:
            await self.driver.close()
            self.logger.info("Neo4j connection closed")
