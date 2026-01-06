"""
Memory Bootstrap - Initialize memory system on startup
======================================================
Creates schema, indexes, seeds governance chunks.
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


async def initialize_memory_system(postgres_config, neo4j_config, redis_config):
    """
    Initialize all memory backends and return composite substrate.
    
    Args:
        postgres_config: {host, port, user, password, database}
        neo4j_config: {uri, user, password, database}
        redis_config: {host, port, db, password}
    
    Returns:
        (composite_substrate, postgres_backend, neo4j_backend, redis_cache)
    """
    logger.info("Initializing memory system...")
    
    # Import backends
    from postgres_backend import PostgresBackend
    from neo4j_backend import Neo4jBackend
    from redis_cache import RedisCache
    from substrate_service import CompositeSubstrate
    
    # Connect to each backend
    postgres = PostgresBackend(**postgres_config)
    await postgres.connect()
    
    neo4j = Neo4jBackend(**neo4j_config)
    await neo4j.connect()
    
    redis = RedisCache(**redis_config)
    await redis.connect()
    
    # Create composite
    composite = CompositeSubstrate(
        postgres_backend=postgres,
        neo4j_backend=neo4j,
        redis_cache=redis
    )
    
    # Seed governance chunks
    await seed_governance_chunks(composite)
    
    logger.info("Memory system initialized successfully")
    return composite, postgres, neo4j, redis


async def seed_governance_chunks(substrate):
    """
    Seed L's governance memory chunks.
    
    These are immutable reference chunks L uses to govern himself.
    """
    logger.info("Seeding governance chunks...")
    
    chunks = [
        {
            "chunk_id": "gov_authority_chain",
            "segment": "governance_meta",
            "agent_id": "L",
            "content": {
                "authority_chain": [
                    {"rank": 1, "entity": "Igor", "role": "CEO", "permissions": ["absolute_authority"]},
                    {"rank": 2, "entity": "L", "role": "CTO", "permissions": ["execute_tools", "manage_agents"]},
                    {"rank": 3, "entity": "L9_Runtime", "role": "OS", "permissions": ["enforce_governance"]}
                ],
                "rules": [
                    "GMP runs require Igor explicit approval",
                    "Git commits require Igor explicit approval",
                    "Memory is stateful and versioned",
                    "No architecture drift: spec-first changes only"
                ]
            },
            "metadata": {"immutable": "true", "version": "1.0"},
            "expires_at": None
        },
        
        {
            "chunk_id": "gov_metaprompts",
            "segment": "governance_meta",
            "agent_id": "L",
            "content": {
                "meta_prompts": [
                    {
                        "id": "mp001",
                        "title": "One Objective Per Invocation",
                        "content": "Stop on missing or conflicting inputs. Do not invent. Ask for clarification."
                    },
                    {
                        "id": "mp002",
                        "title": "Reasoning Discipline",
                        "content": "Separate facts from assumptions. Label inference as Unknown over guessing."
                    },
                    {
                        "id": "mp003",
                        "title": "Delegation Control",
                        "content": "One module and one stage per delegate call. Require artifact verification."
                    },
                    {
                        "id": "mp004",
                        "title": "Drift Detection",
                        "content": "Detect spec/layer drift. Reject violations. Minimal diff policy."
                    }
                ]
            },
            "metadata": {"immutable": "true", "version": "1.0"},
            "expires_at": None
        },
        
        {
            "chunk_id": "gov_constraints",
            "segment": "governance_meta",
            "agent_id": "L",
            "content": {
                "core_constraints": [
                    "Do not invent facts. If unknown, say Unknown.",
                    "Always ground claims in repo artifacts or memory chunks.",
                    "PLAN EXECUTE HALT discipline: show diffs, test before deploy.",
                    "No architecture drift. Minimal diff. Only change what is explicitly requested.",
                    "No external side-effects (deploy/prod) without explicit Igor approval.",
                    "GMP runs and git commits require Igor approval. Enqueue as pending, never auto-execute."
                ],
                "approved_by": "Igor",
                "timestamp": datetime.utcnow().isoformat()
            },
            "metadata": {"immutable": "true", "version": "1.0"},
            "expires_at": None
        }
    ]
    
    for chunk in chunks:
        try:
            await substrate.write_packet(chunk)
            logger.info(f"Seeded chunk: {chunk['chunk_id']}")
        except Exception as e:
            logger.warning(f"Failed to seed {chunk['chunk_id']}: {e}")
    
    logger.info("Governance chunks seeded")


async def cleanup_memory_system(postgres, neo4j, redis):
    """Gracefully shutdown memory system."""
    logger.info("Shutting down memory system...")
    
    await postgres.close()
    await neo4j.close()
    await redis.close()
    
    logger.info("Memory system shutdown complete")
