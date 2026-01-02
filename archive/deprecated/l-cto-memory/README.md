# Deprecated L-CTO Memory Clients

This directory contains deprecated memory client implementations that have been replaced by the canonical L9 memory substrate.

## Archived Files

### `memory_client.py`
- **Status**: DEPRECATED
- **Reason**: Uses Supabase, which has been deprecated in favor of PostgreSQL + Neo4j memory substrate
- **Replacement**: Use `memory.substrate_service.MemorySubstrateService` with `PacketEnvelope` model
- **Archived**: 2025-12-27

### `kg_client.py`
- **Status**: DEPRECATED
- **Reason**: Duplicate of canonical `memory.graph_client.Neo4jClient` (which is async and more feature-rich)
- **Replacement**: Use `memory.graph_client.Neo4jClient` for all Neo4j operations
- **Archived**: 2025-12-27

## Migration Notes

All L-CTO memory operations should now use:
- `memory.substrate_service.MemorySubstrateService` for packet ingestion
- `memory.graph_client.Neo4jClient` for Neo4j graph operations
- `PacketEnvelope` model for all memory writes

See `memory/WIRING.md` for production wiring details.

