# L9 Runtime Spine Map

How work flows through the L9 system from entrypoint to persistence.

---

## Primary Execution Spine

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            ENTRYPOINT                                        │
│                                                                              │
│  uvicorn api.server:app                                                      │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │  api/server.py                                                   │        │
│  │                                                                  │        │
│  │  lifespan() startup:                                            │        │
│  │    1. run_migrations(database_url)  ─────► migrations/*.sql     │        │
│  │    2. init_service(database_url)    ─────► memory substrate     │        │
│  │                                                                  │        │
│  │  app = FastAPI(lifespan=lifespan)                               │        │
│  └─────────────────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Routers mounted
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ROUTERS                                         │
│                                                                              │
│  /os/*        ─────► api/os_routes.py         (health, metrics)             │
│  /agent/*     ─────► api/agent_routes.py      (task management)             │
│  /memory/*    ─────► api/memory/router.py     (packet CRUD, search)         │
│  /world-model/* ──► api/world_model_api.py    (entity, timeline, query)     │
│  /ws/agent    ─────► WebSocket handler        (real-time agent comms)       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ WebSocket path
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         WEBSOCKET LAYER                                      │
│                                                                              │
│  @app.websocket("/ws/agent")                                                 │
│       │                                                                      │
│       ▼                                                                      │
│  1. Receive handshake (AgentHandshake)                                      │
│  2. ws_orchestrator.register(agent_id, websocket, metadata)                 │
│       │                                                                      │
│       ▼                                                                      │
│  3. Message loop:                                                            │
│     ┌──────────────────────────────────────────────────────────────┐        │
│     │  data = await websocket.receive_json()                        │        │
│     │       │                                                       │        │
│     │       ├──► ingest_packet(PacketEnvelopeIn)  ─► Memory DAG    │        │
│     │       │                                                       │        │
│     │       └──► ws_orchestrator.handle_incoming(agent_id, data)   │        │
│     │                   │                                           │        │
│     │                   ▼                                           │        │
│     │            orchestrators/ws_bridge.py                         │        │
│     │                   │                                           │        │
│     │                   ▼                                           │        │
│     │            TaskEnvelope ──► runtime/task_queue.py            │        │
│     └──────────────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Packet ingestion
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MEMORY SUBSYSTEM                                     │
│                                                                              │
│  memory/ingestion.py::ingest_packet(PacketEnvelopeIn)                       │
│       │                                                                      │
│       ▼                                                                      │
│  memory/substrate_graph.py::SubstrateDAG.run(envelope)                      │
│       │                                                                      │
│       │  LangGraph DAG Pipeline:                                            │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────┐                    │
│  │ intake_node │ → │ reasoning_  │ → │ memory_write_   │                    │
│  │             │   │    node     │   │     node        │                    │
│  └─────────────┘   └─────────────┘   └─────────────────┘                    │
│       │                                      │                               │
│       │                                      ▼                               │
│       │                              ┌─────────────────┐                    │
│       │                              │ semantic_embed_ │                    │
│       │                              │     node        │                    │
│       │                              └─────────────────┘                    │
│       │                                      │                               │
│       ▼                                      ▼                               │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐            │
│  │ extract_        │ → │ store_insights_ │ → │ world_model_    │            │
│  │ insights_node   │   │     node        │   │ trigger_node    │            │
│  └─────────────────┘   └─────────────────┘   └─────────────────┘            │
│                                                     │                        │
│                                                     ▼                        │
│                                              ┌─────────────────┐            │
│                                              │ checkpoint_node │            │
│                                              └─────────────────┘            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ DB writes
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PERSISTENCE LAYER                                    │
│                                                                              │
│  memory/substrate_repository.py                                              │
│       │                                                                      │
│       ▼                                                                      │
│  PostgreSQL + pgvector                                                       │
│       │                                                                      │
│       ├── packet_store              (all packets)                            │
│       ├── agent_memory_events       (agent activity log)                     │
│       ├── reasoning_traces          (structured reasoning blocks)            │
│       ├── semantic_memory           (vector embeddings)                      │
│       ├── knowledge_facts           (extracted facts)                        │
│       ├── graph_checkpoints         (DAG state snapshots)                    │
│       └── schema_migrations         (migration tracking)                     │
│                                                                              │
│  world_model/repository.py                                                   │
│       │                                                                      │
│       ├── world_model_entities      (entities in world model)                │
│       ├── world_model_updates       (update history)                         │
│       └── world_model_snapshots     (point-in-time snapshots)                │
└─────────────────────────────────────────────────────────────────────────────┘

---

## Orchestrator Layer

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATORS                                        │
│                                                                              │
│  orchestration/unified_controller.py                                         │
│       │                                                                      │
│       ├── MetaOrchestrator         (high-level coordination)                │
│       ├── WorldModelOrchestrator   (world model lifecycle)                  │
│       ├── MemoryOrchestrator       (memory operations)                      │
│       ├── ReasoningOrchestrator    (inference chains)                       │
│       ├── ResearchSwarmOrchestrator (multi-agent research)                  │
│       ├── EvolutionOrchestrator    (system evolution)                       │
│       └── ActionToolOrchestrator   (tool execution)                         │
│                                                                              │
│  orchestrators/ws_bridge.py                                                  │
│       │                                                                      │
│       └── event_to_task()          (WS event → TaskEnvelope)                │
└─────────────────────────────────────────────────────────────────────────────┘

---

## World Model Subsystem

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         WORLD MODEL                                          │
│                                                                              │
│  world_model/runtime.py::WorldModelRuntime                                   │
│       │                                                                      │
│       ├── world_model/engine.py::WorldModelEngine                           │
│       │       │                                                              │
│       │       ├── Entity management                                         │
│       │       ├── Relationship tracking                                     │
│       │       └── Belief propagation                                        │
│       │                                                                      │
│       ├── world_model/service.py::WorldModelService                         │
│       │       │                                                              │
│       │       └── update_from_insights()  ◄── memory/substrate_graph.py    │
│       │                                                                      │
│       └── simulation/simulation_engine.py                                   │
│               │                                                              │
│               └── Scenario simulation                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Key Singleton Instances

| Singleton | Module | Purpose |
|-----------|--------|---------|
| `ws_orchestrator` | `runtime.websocket_orchestrator` | WebSocket connection manager |
| `_service` | `memory.substrate_service` | Memory substrate singleton |
| `_repository` | `memory.substrate_repository` | DB connection pool |
| `_world_model_engine` | `world_model.engine` | World model singleton |

---

## Startup Sequence

1. `uvicorn api.server:app`
2. `lifespan()` context manager enters
3. `run_migrations()` - apply pending SQL migrations
4. `init_service()` - initialize memory substrate
5. FastAPI app serves requests
6. On shutdown: `close_service()` - cleanup

---

*End of Runtime Spine Map*

