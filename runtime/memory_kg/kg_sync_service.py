"""
KG Sync Service - Supabase to Neo4j synchronization

v3.6.1 Gap Fill Patch:
- Implemented batch sync for efficiency
- Added per-record error recovery
- Enhanced error handling with detailed status
- Added sync statistics and metrics
"""
from neo4j import GraphDatabase
from supabase import create_client
import logging

logger = logging.getLogger(__name__)


class KGSyncService:
    """
    Knowledge Graph Sync Service
    
    Syncs memory events from Supabase to Neo4j for graph-based querying.
    """
    
    def __init__(self, supabase_url: str, supabase_key: str, neo4j_uri: str, neo4j_user: str, neo4j_pass: str):
        """
        Initialize sync service.
        
        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase service role key
            neo4j_uri: Neo4j connection URI
            neo4j_user: Neo4j username
            neo4j_pass: Neo4j password
        """
        self.sb = create_client(supabase_url, supabase_key)
        self.neo = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_pass))
        logger.info("KG Sync Service initialized")
    
    def sync_once(self) -> dict:
        """
        Perform one-time sync from Supabase to Neo4j with full error handling.
        
        Returns:
            Sync result with detailed status
        """
        logger.info("Starting KG sync...")
        
        try:
            # Fetch from Supabase
            try:
                records = self.sb.table("l_memory").select("*").execute().data
                logger.info(f"Fetched {len(records)} records from Supabase")
            except Exception as e:
                logger.error(f"Supabase fetch failed: {e}")
                return {
                    "success": False,
                    "error": f"Supabase fetch failed: {str(e)}",
                    "synced": 0,
                    "total": 0
                }
            
            # Write to Neo4j
            synced_count = 0
            failed_count = 0
            
            with self.neo.session() as session:
                for record in records:
                    try:
                        # Check if record has graph data
                        if "graph" in record and record["graph"]:
                            # Sync nodes
                            for node in record["graph"].get("nodes", []):
                                try:
                                    session.run("""
                                        MERGE (n:Memory {id: $id})
                                        SET n += $props
                                    """, id=node.get("id"), props=node)
                                except Exception as node_error:
                                    logger.warning(f"Node sync failed: {node_error}")
                            
                            # Sync edges
                            for edge in record["graph"].get("edges", []):
                                try:
                                    session.run("""
                                        MATCH (a:Memory {id: $src}), (b:Memory {id: $dst})
                                        MERGE (a)-[r:REL {type: $type}]->(b)
                                    """, src=edge.get("source"), dst=edge.get("target"), type=edge.get("type"))
                                except Exception as edge_error:
                                    logger.warning(f"Edge sync failed: {edge_error}")
                            
                            synced_count += 1
                        else:
                            # Simple record without graph structure
                            if "id" in record:
                                session.run("""
                                    MERGE (n:Memory {id: $id})
                                    SET n += $props
                                """, id=record["id"], props=record)
                                synced_count += 1
                    
                    except Exception as record_error:
                        logger.warning(f"Record sync failed: {record_error}")
                        failed_count += 1
            
            logger.info(f"KG sync complete: {synced_count} synced, {failed_count} failed")
            
            return {
                "success": True,
                "synced": synced_count,
                "failed": failed_count,
                "total": len(records)
            }
            
        except Exception as e:
            logger.exception(f"KG sync failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "synced": 0,
                "total": 0
            }
    
    def run_loop(self, interval: int = 60):
        """
        Run continuous sync loop.
        
        Args:
            interval: Sync interval in seconds
        """
        import time
        
        logger.info(f"Starting KG sync loop (interval: {interval}s)")
        
        while True:
            try:
                self.sync_once()
                time.sleep(interval)
            except KeyboardInterrupt:
                logger.info("KG sync loop stopped")
                break
            except Exception as e:
                logger.error(f"Sync loop error: {e}")
                time.sleep(interval)
    
    def sync_batch(self, batch_size: int = 100) -> dict:
        """
        Perform batch sync for efficiency.
        
        Args:
            batch_size: Number of records per batch
            
        Returns:
            Batch sync result
        """
        logger.info(f"Starting batch KG sync (batch_size={batch_size})...")
        
        try:
            # Fetch all records
            records = self.sb.table("l_memory").select("*").execute().data
            total_records = len(records)
            logger.info(f"Fetched {total_records} records")
            
            # Process in batches
            synced_total = 0
            failed_total = 0
            
            for i in range(0, total_records, batch_size):
                batch = records[i:i + batch_size]
                logger.info(f"Processing batch {i // batch_size + 1} ({len(batch)} records)...")
                
                batch_synced = 0
                batch_failed = 0
                
                with self.neo.session() as session:
                    for record in batch:
                        try:
                            if "id" in record:
                                session.run("""
                                    MERGE (n:Memory {id: $id})
                                    SET n += $props
                                """, id=record["id"], props=record)
                                batch_synced += 1
                        except Exception as e:
                            logger.debug(f"Record sync failed: {e}")
                            batch_failed += 1
                
                synced_total += batch_synced
                failed_total += batch_failed
                logger.info(f"Batch complete: {batch_synced} synced, {batch_failed} failed")
            
            logger.info(f"Batch sync complete: {synced_total}/{total_records} synced")
            
            return {
                "success": True,
                "synced": synced_total,
                "failed": failed_total,
                "total": total_records,
                "batches": (total_records + batch_size - 1) // batch_size
            }
            
        except Exception as e:
            logger.exception(f"Batch sync failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def close(self):
        """Close connections."""
        self.neo.close()

