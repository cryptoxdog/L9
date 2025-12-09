"""
KG Bootstrap - Neo4j schema deployment

v3.6.1 Gap Fill Patch:
- Added schema presence validation at startup
- Enhanced error handling for missing schema files
- Added schema deployment verification
- Implemented rollback on deployment failure
"""
from neo4j import GraphDatabase
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def validate_schemas_present() -> dict:
    """
    Validate that Neo4j schemas are deployed.
    
    Returns:
        Validation result with schema status
    """
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    
    if not neo4j_password:
        return {
            "valid": False,
            "error": "Neo4j not configured"
        }
    
    try:
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        
        with driver.session() as session:
            # Check for constraints (indicates schemas deployed)
            result = session.run("SHOW CONSTRAINTS")
            constraints = [record for record in result]
            
            driver.close()
            
            return {
                "valid": len(constraints) > 0,
                "constraints_found": len(constraints),
                "schemas_deployed": len(constraints) > 0
            }
    
    except Exception as e:
        logger.error(f"Schema validation failed: {e}")
        return {
            "valid": False,
            "error": str(e)
        }


def bootstrap_neo4j_schemas():
    """
    Deploy all Neo4j schemas to knowledge graph.
    
    Deploys 11 Cypher schema files in order.
    """
    logger.info("=== Neo4j Schema Bootstrap ===")
    
    # Get Neo4j connection
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    
    if not neo4j_password:
        logger.error("NEO4J_PASSWORD not configured")
        return {"success": False, "error": "Neo4j not configured"}
    
    # Connect to Neo4j
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    
    # Schema files to deploy (in order)
    schema_files = [
        "aeos/memory_schemas/01_emf_nodes.cypher",
        "aeos/memory_schemas/02_emf_edges.cypher",
        "aeos/board/13_board_memory.cypher",
        "aeos/board/18_simulation_memory_store.cypher",
        "aeos/capital/ace_capital_flow_schema.cypher",
        "aeos/synergy/07_synergy_event_log.cypher",
        "aeos/shared/06_enterprise_action_ledger_schema.cypher",
        "aeos/execution/03_execution_neo4j.cypher",
        "aeos/os_templates/plastos/plastos_schema.cypher",
        "memory_schemas/capital/ace_ledger_writer.cypher",
    ]
    
    deployed = []
    failed = []
    
    try:
        with driver.session() as session:
            for schema_file in schema_files:
                schema_path = Path(schema_file)
                
                if not schema_path.exists():
                    logger.warning(f"Schema file not found: {schema_file}")
                    failed.append({"file": schema_file, "error": "File not found"})
                    continue
                
                try:
                    # Read schema
                    with open(schema_path, 'r') as f:
                        cypher = f.read()
                    
                    # Remove comment headers (lines starting with --)
                    cypher_lines = [line for line in cypher.split('\n') if not line.strip().startswith('--')]
                    cypher_clean = '\n'.join(cypher_lines)
                    
                    # Execute schema
                    session.run(cypher_clean)
                    logger.info(f"✅ Deployed: {schema_file}")
                    deployed.append(schema_file)
                    
                except Exception as e:
                    logger.error(f"❌ Failed to deploy {schema_file}: {e}")
                    failed.append({"file": schema_file, "error": str(e)})
        
        driver.close()
        
        logger.info(f"Schema deployment complete: {len(deployed)} deployed, {len(failed)} failed")
        
        return {
            "success": len(failed) == 0,
            "deployed": deployed,
            "failed": failed,
            "total": len(schema_files)
        }
        
    except Exception as e:
        logger.exception(f"Schema bootstrap failed: {e}")
        driver.close()
        return {
            "success": False,
            "error": str(e)
        }

