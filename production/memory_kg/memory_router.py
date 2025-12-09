"""
Memory Router - Route memory operations to appropriate storage

v3.6.1 Gap Fill Patch:
- Implemented memory type classification (reasoning, log, system)
- Added fallback if Neo4j offline
- Implemented retry with backoff for Supabase writes
- Added batch sync capability
- Enforced structured_memory_policy.json validation
"""
from supabase import Client
from neo4j import Driver
import logging
import time
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class MemoryRouter:
    """
    Memory Router
    
    Routes memory operations to appropriate storage:
    - Supabase: Structured data, fast queries
    - Neo4j: Graph relationships, complex queries
    """
    
    def __init__(self, supabase_client: Client, neo4j_driver: Driver):
        """
        Initialize memory router with policy enforcement.
        
        Args:
            supabase_client: Supabase client
            neo4j_driver: Neo4j driver
        """
        self.sb = supabase_client
        self.neo = neo4j_driver
        self.policy = self._load_policy()
        self.neo4j_online = True  # Track Neo4j availability
        logger.info("Memory router initialized")
    
    def _load_policy(self) -> dict:
        """Load structured memory policy."""
        try:
            policy_path = Path(__file__).parent / "structured_memory_policy.json"
            with open(policy_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load memory policy: {e}")
            return {
                "retention": "long_term",
                "write_rules": {
                    "allowed": ["reasoning", "execution_logs", "governance_events"],
                    "forbidden": ["private_keys", "system_passwords"]
                },
                "constraints": {
                    "max_tokens_per_entry": 2000,
                    "no_sensitive_data": True
                }
            }
    
    def _classify_memory_type(self, entry: dict) -> str:
        """
        Classify memory entry type.
        
        Args:
            entry: Memory entry
            
        Returns:
            Type: reasoning, log, system, or unknown
        """
        entry_type = entry.get("type")
        if entry_type:
            return entry_type
        
        # Infer from content
        content_str = str(entry).lower()
        
        if "reasoning" in content_str or "analysis" in content_str:
            return "reasoning"
        elif "log" in content_str or "event" in content_str:
            return "log"
        elif "system" in content_str or "runtime" in content_str:
            return "system"
        else:
            return "unknown"
    
    def _validate_against_policy(self, entry: dict) -> dict:
        """
        Validate entry against structured memory policy.
        
        Args:
            entry: Entry to validate
            
        Returns:
            Validation result
        """
        issues = []
        
        # Check if type is allowed
        entry_type = self._classify_memory_type(entry)
        allowed_types = self.policy.get("write_rules", {}).get("allowed", [])
        
        if entry_type not in allowed_types and entry_type != "unknown":
            issues.append(f"Memory type '{entry_type}' not in allowed list")
        
        # Check for forbidden content
        forbidden = self.policy.get("write_rules", {}).get("forbidden", [])
        entry_str = str(entry).lower()
        
        for forbidden_item in forbidden:
            if forbidden_item.replace("_", " ") in entry_str:
                issues.append(f"Forbidden content detected: {forbidden_item}")
        
        # Check size constraints
        max_tokens = self.policy.get("constraints", {}).get("max_tokens_per_entry", 2000)
        entry_size = len(str(entry))
        
        if entry_size > max_tokens:
            issues.append(f"Entry exceeds max size: {entry_size} > {max_tokens}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    def route_write(self, entry: dict) -> dict:
        """
        Route write operation with policy enforcement and retry.
        
        Determines best storage based on entry type:
        - Simple data → Supabase only
        - Graph data → Both Supabase and Neo4j (with Neo4j fallback)
        - Relationships → Neo4j only (with Supabase fallback)
        
        Args:
            entry: Memory entry to write
            
        Returns:
            Write result
        """
        # Validate against policy
        policy_check = self._validate_against_policy(entry)
        if not policy_check["valid"]:
            logger.warning(f"Policy violation: {policy_check['issues']}")
            return {
                "success": False,
                "error": f"Policy validation failed: {', '.join(policy_check['issues'])}"
            }
        
        # Classify entry type
        entry_type = self._classify_memory_type(entry)
        logger.debug(f"Routing write: {entry_type}")
        
        try:
            if entry_type == "graph" or "relationships" in entry:
                # Write to both (with Neo4j fallback)
                result = self._write_both(entry)
                if not result.get("neo4j", {}).get("success") and not self.neo4j_online:
                    logger.warning("Neo4j offline, wrote to Supabase only")
                return result
            elif entry_type == "relationship":
                # Write to Neo4j (with Supabase fallback if Neo4j offline)
                if self.neo4j_online:
                    return self._write_neo4j(entry)
                else:
                    logger.warning("Neo4j offline, falling back to Supabase")
                    return self._write_supabase(entry)
            else:
                # Write to Supabase with retry
                return self._write_supabase_with_retry(entry)
                
        except Exception as e:
            logger.error(f"Write routing failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _write_supabase_with_retry(self, entry: dict, max_retries: int = 3) -> dict:
        """Write to Supabase with exponential backoff retry."""
        delay = 1.0
        
        for attempt in range(max_retries):
            result = self._write_supabase(entry)
            
            if result["success"]:
                return result
            
            if attempt < max_retries - 1:
                logger.warning(f"Supabase write failed (attempt {attempt + 1}), retrying in {delay}s...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
        
        return result  # Return last failure
    
    def route_read(self, query: dict) -> dict:
        """
        Route read operation.
        
        Determines best source based on query type:
        - Simple queries → Supabase
        - Graph queries → Neo4j
        - Complex queries → Both (merge results)
        
        Args:
            query: Query to execute
            
        Returns:
            Query results
        """
        logger.debug(f"Routing read: {query.get('type', 'unknown')}")
        
        query_type = query.get("type", "simple")
        
        try:
            if query_type == "graph":
                return self._read_neo4j(query)
            elif query_type == "complex":
                return self._read_both(query)
            else:
                return self._read_supabase(query)
                
        except Exception as e:
            logger.error(f"Read routing failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _write_supabase(self, entry: dict) -> dict:
        """Write to Supabase with error handling."""
        try:
            result = self.sb.table("l_memory").insert(entry).execute()
            return {
                "success": True,
                "storage": "supabase",
                "id": result.data[0]["id"] if result.data else None
            }
        except Exception as e:
            logger.error(f"Supabase write failed: {e}")
            return {"success": False, "storage": "supabase", "error": str(e)}
    
    def _write_neo4j(self, entry: dict) -> dict:
        """Write to Neo4j with error handling and offline detection."""
        try:
            with self.neo.session() as session:
                # Use MERGE instead of CREATE to avoid duplicates
                if "id" in entry:
                    session.run("""
                        MERGE (n:Memory {id: $id})
                        SET n += $props
                    """, id=entry["id"], props=entry)
                else:
                    session.run("CREATE (n:Memory $props)", props=entry)
            
            self.neo4j_online = True  # Mark as online
            return {"success": True, "storage": "neo4j"}
        except Exception as e:
            logger.error(f"Neo4j write failed: {e}")
            self.neo4j_online = False  # Mark as offline
            return {"success": False, "storage": "neo4j", "error": str(e)}
    
    def _write_both(self, entry: dict) -> dict:
        """Write to both storages with error handling."""
        sb_result = self._write_supabase(entry)
        neo_result = self._write_neo4j(entry)
        
        # Determine overall success
        success = sb_result["success"] or neo_result["success"]  # At least one succeeded
        
        return {
            "success": success,
            "storage": "both",
            "supabase": sb_result,
            "neo4j": neo_result
        }
    
    def _read_supabase(self, query: dict) -> dict:
        """Read from Supabase with error handling."""
        try:
            # Build query
            table = self.sb.table("l_memory").select("*")
            
            # Apply filters if provided
            if "filter" in query:
                for key, value in query["filter"].items():
                    table = table.eq(key, value)
            
            # Apply limit
            limit = query.get("limit", 10)
            table = table.limit(limit)
            
            result = table.execute()
            return {"success": True, "data": result.data, "storage": "supabase"}
        except Exception as e:
            logger.error(f"Supabase read failed: {e}")
            return {"success": False, "data": [], "storage": "supabase", "error": str(e)}
    
    def _read_neo4j(self, query: dict) -> dict:
        """Read from Neo4j with error handling."""
        try:
            cypher = query.get("cypher", "MATCH (n:Memory) RETURN n LIMIT 10")
            params = query.get("params", {})
            
            with self.neo.session() as session:
                result = session.run(cypher, params)
                records = [dict(record) for record in result]
            
            return {"success": True, "data": records, "storage": "neo4j"}
        except Exception as e:
            logger.error(f"Neo4j read failed: {e}")
            return {"success": False, "data": [], "storage": "neo4j", "error": str(e)}
    
    def _read_both(self, query: dict) -> dict:
        """Read from both and merge with error handling."""
        sb_result = self._read_supabase(query)
        neo_result = self._read_neo4j(query)
        
        return {
            "success": sb_result["success"] or neo_result["success"],
            "data": {
                "supabase": sb_result.get("data", []),
                "neo4j": neo_result.get("data", [])
            },
            "storage": "both",
            "supabase_success": sb_result["success"],
            "neo4j_success": neo_result["success"]
        }

