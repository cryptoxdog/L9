"""
L9 Memory - Neo4j Graph Client
===============================

Production Neo4j client for L9 knowledge graph operations.

Provides:
- Entity graph storage and traversal
- Relationship management
- Event timeline queries
- Knowledge fact storage

Version: 1.0.0
"""

from __future__ import annotations

import structlog
import os
from typing import Any, Optional

logger = structlog.get_logger(__name__)

# Try to import Neo4j driver
try:
    from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession, basic_auth
    from neo4j.exceptions import ServiceUnavailable, AuthError

    _has_neo4j = True
except ImportError:
    _has_neo4j = False
    logger.warning(
        "Neo4j driver not available - install with: pip install neo4j>=5.0.0"
    )


class Neo4jClient:
    """
    Production Neo4j client with connection management.

    Provides async graph database operations for the L9 memory layer.
    """

    def __init__(
        self,
        uri: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: str = "neo4j",
    ):
        """
        Initialize Neo4j client.

        Args:
            uri: Neo4j URI (default: NEO4J_URI env or 'bolt://localhost:7687')
            user: Neo4j username (default: NEO4J_USER env or 'neo4j')
            password: Neo4j password (default: NEO4J_PASSWORD env)
            database: Database name (default: 'neo4j')
        """
        if not _has_neo4j:
            self._driver = None
            self._available = False
            logger.warning(
                "Neo4j driver not available - operations will fail gracefully"
            )
            return

        self._uri = uri or os.getenv("NEO4J_URL") or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self._user = user or os.getenv("NEO4J_USER", "neo4j")
        self._password = password or os.getenv("NEO4J_PASSWORD")
        self._database = database
        self._driver: Optional[AsyncDriver] = None
        self._available = False

    async def connect(self) -> bool:
        """
        Connect to Neo4j server.

        Returns:
            True if connected, False if unavailable
        """
        if not _has_neo4j:
            return False

        if self._driver is not None:
            return self._available

        if not self._password:
            logger.warning("NEO4J_PASSWORD not set - cannot connect to Neo4j")
            return False

        try:
            self._driver = AsyncGraphDatabase.driver(
                self._uri,
                auth=basic_auth(self._user, self._password),
            )

            # Test connection
            async with self._driver.session(database=self._database) as session:
                await session.run("RETURN 1")

            self._available = True
            logger.info(f"Neo4j connected: {self._uri}/{self._database}")
            return True
        except (ServiceUnavailable, AuthError) as e:
            logger.warning(f"Neo4j connection failed: {e}")
            self._driver = None
            self._available = False
            return False
        except Exception as e:
            logger.warning(f"Neo4j connection failed: {e}")
            self._driver = None
            self._available = False
            return False

    async def disconnect(self) -> None:
        """Close Neo4j connection."""
        if self._driver:
            try:
                await self._driver.close()
                logger.info("Neo4j disconnected")
            except Exception as e:
                logger.warning(f"Error disconnecting Neo4j: {e}")
            finally:
                self._driver = None
                self._available = False

    def is_available(self) -> bool:
        """Check if Neo4j is available."""
        return self._available and self._driver is not None

    @property
    def driver(self) -> Optional[AsyncDriver]:
        """Expose the raw AsyncDriver for components that need it (e.g., AgentGraphLoader)."""
        return self._driver

    def session(self, database: Optional[str] = None) -> AsyncSession:
        """Create a session (AsyncDriver-compatible interface).
        
        This allows Neo4jClient to be used where an AsyncDriver is expected.
        """
        if not self._driver:
            raise RuntimeError("Neo4j driver not initialized")
        db = database or self._database
        return self._driver.session(database=db)

    async def _get_session(self) -> Optional[AsyncSession]:
        """Get a session for database operations."""
        if not self.is_available():
            return None
        return self._driver.session(database=self._database)

    # =========================================================================
    # Entity Operations
    # =========================================================================

    async def create_entity(
        self,
        entity_type: str,
        entity_id: str,
        properties: dict[str, Any],
    ) -> Optional[str]:
        """
        Create or merge an entity node.

        Args:
            entity_type: Node label (e.g., 'User', 'Agent', 'Event')
            entity_id: Unique entity identifier
            properties: Node properties

        Returns:
            Entity ID or None if failed
        """
        if not self.is_available():
            return None

        try:
            async with self._driver.session(database=self._database) as session:
                query = f"""
                MERGE (n:{entity_type} {{id: $entity_id}})
                SET n += $properties
                RETURN n.id as id
                """
                result = await session.run(
                    query,
                    entity_id=entity_id,
                    properties=properties,
                )
                record = await result.single()
                logger.debug(f"Created/updated entity: {entity_type}:{entity_id}")
                return record["id"] if record else None
        except Exception as e:
            logger.error(f"Neo4j create_entity failed: {e}")
            return None

    async def get_entity(
        self,
        entity_type: str,
        entity_id: str,
    ) -> Optional[dict[str, Any]]:
        """
        Get an entity by type and ID.

        Args:
            entity_type: Node label
            entity_id: Entity identifier

        Returns:
            Entity properties or None
        """
        if not self.is_available():
            return None

        try:
            async with self._driver.session(database=self._database) as session:
                query = f"""
                MATCH (n:{entity_type} {{id: $entity_id}})
                RETURN n
                """
                result = await session.run(query, entity_id=entity_id)
                record = await result.single()
                if record:
                    return dict(record["n"])
                return None
        except Exception as e:
            logger.error(f"Neo4j get_entity failed: {e}")
            return None

    async def delete_entity(
        self,
        entity_type: str,
        entity_id: str,
    ) -> bool:
        """
        Delete an entity and its relationships.

        Args:
            entity_type: Node label
            entity_id: Entity identifier

        Returns:
            True if deleted
        """
        if not self.is_available():
            return False

        try:
            async with self._driver.session(database=self._database) as session:
                query = f"""
                MATCH (n:{entity_type} {{id: $entity_id}})
                DETACH DELETE n
                """
                await session.run(query, entity_id=entity_id)
                logger.debug(f"Deleted entity: {entity_type}:{entity_id}")
                return True
        except Exception as e:
            logger.error(f"Neo4j delete_entity failed: {e}")
            return False

    # =========================================================================
    # Relationship Operations
    # =========================================================================

    async def create_relationship(
        self,
        from_type: str,
        from_id: str,
        to_type: str,
        to_id: str,
        rel_type: str,
        properties: Optional[dict[str, Any]] = None,
    ) -> bool:
        """
        Create a relationship between two entities.

        Args:
            from_type: Source node label
            from_id: Source entity ID
            to_type: Target node label
            to_id: Target entity ID
            rel_type: Relationship type (e.g., 'KNOWS', 'TRIGGERED', 'PART_OF')
            properties: Optional relationship properties

        Returns:
            True if created
        """
        if not self.is_available():
            return False

        try:
            async with self._driver.session(database=self._database) as session:
                props = properties or {}
                query = f"""
                MATCH (a:{from_type} {{id: $from_id}})
                MATCH (b:{to_type} {{id: $to_id}})
                MERGE (a)-[r:{rel_type}]->(b)
                SET r += $properties
                RETURN type(r) as rel
                """
                result = await session.run(
                    query,
                    from_id=from_id,
                    to_id=to_id,
                    properties=props,
                )
                record = await result.single()
                if record:
                    logger.debug(
                        f"Created relationship: {from_type}:{from_id} -[{rel_type}]-> {to_type}:{to_id}"
                    )
                    return True
                return False
        except Exception as e:
            logger.error(f"Neo4j create_relationship failed: {e}")
            return False

    async def get_relationships(
        self,
        entity_type: str,
        entity_id: str,
        rel_type: Optional[str] = None,
        direction: str = "both",
    ) -> list[dict[str, Any]]:
        """
        Get relationships for an entity.

        Args:
            entity_type: Node label
            entity_id: Entity identifier
            rel_type: Optional filter by relationship type
            direction: 'outgoing', 'incoming', or 'both'

        Returns:
            List of relationships with connected nodes
        """
        if not self.is_available():
            return []

        try:
            async with self._driver.session(database=self._database) as session:
                rel_pattern = f":{rel_type}" if rel_type else ""

                if direction == "outgoing":
                    query = f"""
                    MATCH (n:{entity_type} {{id: $entity_id}})-[r{rel_pattern}]->(m)
                    RETURN type(r) as rel_type, properties(r) as rel_props, labels(m) as target_labels, m.id as target_id, properties(m) as target_props
                    """
                elif direction == "incoming":
                    query = f"""
                    MATCH (n:{entity_type} {{id: $entity_id}})<-[r{rel_pattern}]-(m)
                    RETURN type(r) as rel_type, properties(r) as rel_props, labels(m) as source_labels, m.id as source_id, properties(m) as source_props
                    """
                else:  # both
                    query = f"""
                    MATCH (n:{entity_type} {{id: $entity_id}})-[r{rel_pattern}]-(m)
                    RETURN type(r) as rel_type, properties(r) as rel_props, labels(m) as connected_labels, m.id as connected_id, properties(m) as connected_props
                    """

                result = await session.run(query, entity_id=entity_id)
                records = await result.data()
                return records
        except Exception as e:
            logger.error(f"Neo4j get_relationships failed: {e}")
            return []

    # =========================================================================
    # Event Timeline Operations
    # =========================================================================

    async def create_event(
        self,
        event_id: str,
        event_type: str,
        timestamp: str,
        properties: dict[str, Any],
        parent_event_id: Optional[str] = None,
    ) -> Optional[str]:
        """
        Create an event in the timeline.

        Args:
            event_id: Unique event identifier
            event_type: Event type (e.g., 'user_action', 'agent_response')
            timestamp: ISO timestamp
            properties: Event properties
            parent_event_id: Optional parent event for causality chain

        Returns:
            Event ID or None
        """
        if not self.is_available():
            return None

        try:
            async with self._driver.session(database=self._database) as session:
                # Create the event
                props = {**properties, "event_type": event_type, "timestamp": timestamp}
                query = """
                MERGE (e:Event {id: $event_id})
                SET e += $properties
                RETURN e.id as id
                """
                result = await session.run(query, event_id=event_id, properties=props)
                await result.single()

                # Link to parent if provided
                if parent_event_id:
                    link_query = """
                    MATCH (parent:Event {id: $parent_id})
                    MATCH (child:Event {id: $child_id})
                    MERGE (parent)-[:TRIGGERED]->(child)
                    """
                    await session.run(
                        link_query,
                        parent_id=parent_event_id,
                        child_id=event_id,
                    )

                logger.debug(f"Created event: {event_type}:{event_id}")
                return event_id
        except Exception as e:
            logger.error(f"Neo4j create_event failed: {e}")
            return None

    async def get_event_timeline(
        self,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Get events in time range.

        Args:
            start_time: ISO timestamp start (optional)
            end_time: ISO timestamp end (optional)
            event_type: Filter by event type (optional)
            limit: Maximum events to return

        Returns:
            List of events ordered by timestamp
        """
        if not self.is_available():
            return []

        try:
            async with self._driver.session(database=self._database) as session:
                conditions = []
                params: dict[str, Any] = {"limit": limit}

                if start_time:
                    conditions.append("e.timestamp >= $start_time")
                    params["start_time"] = start_time
                if end_time:
                    conditions.append("e.timestamp <= $end_time")
                    params["end_time"] = end_time
                if event_type:
                    conditions.append("e.event_type = $event_type")
                    params["event_type"] = event_type

                where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

                query = f"""
                MATCH (e:Event)
                {where_clause}
                RETURN e
                ORDER BY e.timestamp DESC
                LIMIT $limit
                """

                result = await session.run(query, **params)
                records = await result.data()
                return [dict(r["e"]) for r in records]
        except Exception as e:
            logger.error(f"Neo4j get_event_timeline failed: {e}")
            return []

    # =========================================================================
    # Query Operations
    # =========================================================================

    async def run_query(
        self,
        query: str,
        parameters: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        """
        Run a custom Cypher query.

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            Query results as list of dicts
        """
        if not self.is_available():
            return []

        try:
            async with self._driver.session(database=self._database) as session:
                result = await session.run(query, **(parameters or {}))
                records = await result.data()
                return records
        except Exception as e:
            logger.error(f"Neo4j run_query failed: {e}")
            return []


# =============================================================================
# Singleton Factory
# =============================================================================

_neo4j_client: Optional[Neo4jClient] = None


async def get_neo4j_client() -> Optional[Neo4jClient]:
    """
    Get or create singleton Neo4j client.

    Returns:
        Neo4jClient instance or None if unavailable
    """
    global _neo4j_client

    if _neo4j_client is None:
        _neo4j_client = Neo4jClient()
        await _neo4j_client.connect()

    return _neo4j_client if _neo4j_client.is_available() else None


async def close_neo4j_client() -> None:
    """Close singleton Neo4j client."""
    global _neo4j_client
    if _neo4j_client:
        await _neo4j_client.disconnect()
        _neo4j_client = None


__all__ = ["Neo4jClient", "get_neo4j_client", "close_neo4j_client"]
