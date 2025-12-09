"""
L KG Client - Neo4j knowledge graph interface
"""
from neo4j import GraphDatabase
import os
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class KGClient:
    """
    Neo4j knowledge graph client for L (CTO).
    
    Provides graph-based knowledge storage and querying.
    """
    
    def __init__(self):
        """Initialize Neo4j driver."""
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
        neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        neo4j_password = os.getenv("NEO4J_PASSWORD")
        
        if not neo4j_password:
            logger.warning("Neo4j password not configured")
            self.driver = None
            self.connected = False
        else:
            self.driver = GraphDatabase.driver(
                neo4j_uri,
                auth=(neo4j_user, neo4j_password)
            )
            self.connected = False
    
    def init(self):
        """Initialize KG client and verify connection with schema existence check."""
        if not self.driver:
            logger.error("Cannot initialize: Neo4j not configured")
            return
        
        try:
            # Test connection
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                result.single()
                
                # Check if schemas exist (check for Memory node constraint)
                schema_check = session.run("""
                    SHOW CONSTRAINTS
                    YIELD name
                    WHERE name CONTAINS 'Memory' OR name CONTAINS 'memory'
                    RETURN count(*) as schema_count
                """)
                schema_result = schema_check.single()
                schema_count = schema_result["schema_count"] if schema_result else 0
                
                if schema_count > 0:
                    logger.info(f"Neo4j schemas detected: {schema_count} constraints found")
                else:
                    logger.warning("No Neo4j schemas detected - run kg_bootstrap.py to deploy")
                
            self.connected = True
            logger.info("KG client initialized successfully")
        except Exception as e:
            logger.error(f"KG client initialization failed: {e}")
            self.connected = False
    
    def upsert(self, node_type: str, data: dict) -> dict:
        """
        Upsert node in knowledge graph.
        
        Args:
            node_type: Node label (e.g., "Agent", "Task", "Memory")
            data: Node properties (must include 'id')
            
        Returns:
            Upsert result
        """
        if not self.connected:
            return {"success": False, "error": "KG client not connected"}
        
        if "id" not in data:
            return {"success": False, "error": "Node data must include 'id'"}
        
        try:
            with self.driver.session() as session:
                query = f"""
                MERGE (n:{node_type} {{id: $id}})
                SET n += $data
                RETURN n
                """
                result = session.run(query, id=data["id"], data=data)
                node = result.single()
                
                return {
                    "success": True,
                    "node": dict(node["n"]) if node else None
                }
        except Exception as e:
            logger.error(f"KG upsert failed: {e}")
            return {"success": False, "error": str(e)}
    
    def query(self, cypher: str, params: dict = None) -> dict:
        """
        Execute Cypher query.
        
        Args:
            cypher: Cypher query string
            params: Query parameters
            
        Returns:
            Query results
        """
        if not self.connected:
            return {"success": False, "error": "KG client not connected"}
        
        try:
            with self.driver.session() as session:
                result = session.run(cypher, params or {})
                records = [dict(record) for record in result]
                
                return {
                    "success": True,
                    "data": records,
                    "count": len(records)
                }
        except Exception as e:
            logger.error(f"KG query failed: {e}")
            return {"success": False, "error": str(e)}
    
    def close(self):
        """Close Neo4j driver connection."""
        if self.driver:
            self.driver.close()
            self.connected = False

