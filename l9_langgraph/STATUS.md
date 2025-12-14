# LangGraph Integration Status

## Current Status: OPTIONAL / NOT WIRED

The `PacketNodeAdapter` exists but is **not automatically wired** into the main execution flow.

## What Exists

- `l9_langgraph/packet_node_adapter.py` - Adapter to wrap LangGraph nodes with memory logging
- Used internally by `memory/substrate_graph.py` for the substrate DAG
- Available for manual integration in custom LangGraph graphs

## Decision

**LangGraph is OPTIONAL** for packet ingestion. The memory system works independently via:
- `memory.ingestion.ingest_packet()` - Canonical entrypoint
- `MemorySubstrateService.write_packet()` - Service layer
- `SubstrateDAG` - Internal LangGraph DAG for processing

## Usage

If you want to use `PacketNodeAdapter` in your own LangGraph graphs:

```python
from langgraph.packet_node_adapter import PacketNodeAdapter
from memory.substrate_service import get_service

service = await get_service()
adapter = PacketNodeAdapter(service, agent_id="my_agent")

# Wrap your node function
async def my_node(state):
    # ... your logic ...
    return new_state

wrapped_node = lambda state: adapter(state, my_node, "my_node")
```

## Future

If LangGraph becomes required for all packet processing, wire `PacketNodeAdapter` into:
- WebSocket event handlers
- API route handlers
- Agent execution loops

For now, packets flow through `ingest_packet()` → `MemorySubstrateService` → `SubstrateDAG`.

