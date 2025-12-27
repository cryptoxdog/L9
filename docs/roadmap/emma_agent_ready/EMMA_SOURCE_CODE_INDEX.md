# Emma Agent Module — Source Code Index & Integration Guide

## Quick Reference: All Generated Files

```
emma_agent/
├── __init__.py                          # Public API, version metadata
├── controller.py                        # Core orchestration (280 lines)
├── schemas.py                           # Pydantic data models (200 lines)
├── config.py                            # Configuration management (220 lines)
│
├── modules/
│   ├── __init__.py
│   ├── memory_manager.py               # Unified memory abstraction (350 lines)
│   ├── embeddings_handler.py           # Vector/embedding management (200 lines)
│   ├── redis_cache.py                  # Redis integration (180 lines)
│   ├── governance_handler.py           # Governance policy enforcement (250 lines)
│   └── escalation_manager.py           # Escalation workflows (200 lines)
│
├── api/
│   ├── __init__.py
│   ├── agent_routes.py                 # Task API endpoints (200 lines)
│   ├── memory_routes.py                # Memory API endpoints (180 lines)
│   └── os_routes.py                    # Health/metrics endpoints (150 lines)
│
├── webhooks/
│   ├── __init__.py
│   ├── slack.py                        # Slack integration (220 lines)
│   ├── twilio.py                       # Twilio integration (180 lines)
│   └── waba.py                         # WhatsApp Business integration (200 lines)
│
├── infra/
│   ├── __init__.py
│   ├── database.py                     # PostgreSQL/asyncpg (280 lines)
│   ├── cache.py                        # Redis integration (150 lines)
│   ├── metrics.py                      # Prometheus metrics (200 lines)
│   └── health.py                       # Health checks (120 lines)
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                     # Pytest fixtures (150 lines)
│   ├── test_controller.py              # Controller tests (280 lines)
│   ├── test_memory.py                  # Memory tests (200 lines)
│   ├── test_governance.py              # Governance tests (180 lines)
│   ├── test_api.py                     # API endpoint tests
│   └── test_webhooks.py                # Webhook tests
│
├── README.md                            # Quick start guide
├── CONFIG.md                            # Configuration reference
├── DEPLOYMENT.md                        # Deployment guide
└── manifest.json                        # Module specification

Total: 28 files, ~5000 lines of production code
```

---

## Core Module Usage Examples

### 1. Initialize Emma Controller

```python
import asyncio
from emma_agent.controller import EmmaController
from emma_agent.modules.memory_manager import MemoryManager
from emma_agent.modules.governance_handler import GovernanceHandler
from emma_agent.modules.escalation_manager import EscalationManager
from emma_agent.infra.database import DatabasePool
from emma_agent.infra.cache import CacheManager
from emma_agent.infra.metrics import MetricsCollector
from emma_agent.infra.health import HealthChecker

async def main():
    # Initialize infrastructure
    db_pool = DatabasePool("postgresql://user:pass@localhost/emma")
    cache_manager = CacheManager("redis://localhost:6379/0")
    
    await db_pool.initialize()
    await cache_manager.initialize()
    
    # Initialize subsystems
    memory_manager = MemoryManager(db_pool, cache_manager)
    governance_handler = GovernanceHandler()
    escalation_manager = EscalationManager()
    metrics_collector = MetricsCollector()
    health_checker = HealthChecker(db_pool, cache_manager, memory_manager)
    
    # Create controller
    controller = EmmaController(
        db_pool=db_pool,
        cache_manager=cache_manager,
        memory_manager=memory_manager,
        governance_handler=governance_handler,
        escalation_manager=escalation_manager,
        metrics_collector=metrics_collector,
        health_checker=health_checker,
    )
    
    await controller.initialize()
    return controller

asyncio.run(main())
```

### 2. Submit and Execute Task

```python
from emma_agent.controller import Task, TaskType
from datetime import datetime

async def execute_task_example():
    controller = await main()
    
    # Create task
    task = Task(
        task_id="task_001",
        task_type=TaskType.RESEARCH,
        description="Analyze market trends in Q4",
        parameters={"domain": "finance", "region": "US"},
        created_at=datetime.utcnow(),
        created_by="user@company.com",
        priority=7,
        estimated_cost=50.0,
    )
    
    # Submit task
    task_id = await controller.submit_task(task)
    print(f"Task submitted: {task_id}")
    
    # Check status
    result = await controller.execute_task(task)
    print(f"Task result: {result}")
    
    await controller.shutdown()
```

### 3. Memory Operations

```python
from emma_agent.modules.memory_manager import MemoryEvent

async def memory_operations_example():
    controller = await main()
    memory_manager = controller.memory_manager
    
    # Store event
    event = MemoryEvent(
        event_id="evt_001",
        agent_id="emma",
        event_type="research_completed",
        timestamp=datetime.utcnow(),
        data={"analysis": "Q4 shows growth of 15%"},
    )
    
    await memory_manager.store_event(event)
    
    # Query events
    events = await memory_manager.query_events(
        query="market trends",
        limit=10,
    )
    
    # Semantic search with embeddings
    results = await memory_manager.similarity_search(
        query_vector=[0.1, 0.2, 0.3, ...],
        limit=5,
    )
    
    # Assemble context for task
    context = await memory_manager.assemble_context(task)
    
    await controller.shutdown()
```

### 4. Governance & Escalation

```python
async def governance_example():
    controller = await main()
    governance = controller.governance_handler
    escalation = controller.escalation_manager
    
    # Evaluate governance gate
    gate_result = await governance.evaluate_gate(task)
    
    if gate_result == "ESCALATE":
        # Create escalation
        escalation_id = await escalation.create_escalation(task)
        
        # Send notification to Igor (compliance officer)
        await escalation.notify_approver(
            escalation_id=escalation_id,
            recipient="igor@company.com",
            subject=f"Escalation: {task.description}",
        )
        
        # Wait for approval
        status = await escalation.wait_for_approval(
            escalation_id=escalation_id,
            timeout_seconds=3600,
        )
    
    await controller.shutdown()
```

### 5. FastAPI Integration

```python
from fastapi import FastAPI, Depends
from emma_agent.api import agent_routes, memory_routes, os_routes

app = FastAPI(title="Emma Agent API")

# Include routers
app.include_router(agent_routes.router, prefix="/api")
app.include_router(memory_routes.router, prefix="/api")
app.include_router(os_routes.router)

# Dependency injection
async def get_controller() -> EmmaController:
    return controller  # Initialized in lifespan

@app.get("/health")
async def health(controller: EmmaController = Depends(get_controller)):
    return await controller.health_check()

# Run with: uvicorn main:app --reload
```

---

## API Endpoint Reference

### Task Management

```
POST /api/tasks
{
  "task_type": "research",
  "description": "Analyze market trends",
  "parameters": {...},
  "priority": 7,
  "estimated_cost": 50.0
}

Response:
{
  "task_id": "task_abc123",
  "status": "accepted",
  "correlation_id": "corr_xyz789"
}

---

GET /api/tasks/{task_id}

Response:
{
  "task_id": "task_abc123",
  "status": "completed",
  "result": {...},
  "duration_seconds": 12.34,
  "correlation_id": "corr_xyz789"
}
```

### Memory Operations

```
POST /api/memory/store
{
  "content": "Q4 market analysis shows 15% growth",
  "source": "slack",
  "metadata": {"channel": "#research"}
}

---

GET /api/memory/search?query=market trends&limit=10

---

POST /api/memory/embeddings
{
  "content": "...",
  "embedding": [0.1, 0.2, 0.3, ...]
}
```

### Health & Metrics

```
GET /health

Response:
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "checks": {
    "database": "ok",
    "cache": "ok",
    "memory": "ok",
    "governance": "ok"
  }
}

---

GET /metrics
(Prometheus format)
```

---

## Webhook Integration Examples

### Slack Command

```
/emma Analyze Q4 financial results
```

Triggers: `SlackCommandHandler.handle_command()`
Routes to: `EmmaController.submit_task()` with TaskType.RESEARCH

### Slack Event

```
@emma What are the market trends?
```

Triggers: `SlackEventHandler.handle_event()`
Routes to: `EmmaController.submit_task()` with context from memory

### Twilio SMS

```
SMS to Emma number: "Remind me of Q4 results"
```

Triggers: `TwilioHandler.handle_sms()`
Routes to: `EmmaController.submit_task()` with TaskType.MEMORY

---

## Database Schema Overview

### PostgreSQL Tables

```sql
-- Episodic memory
CREATE TABLE episodic_memory (
  event_id UUID PRIMARY KEY,
  agent_id VARCHAR(255),
  event_type VARCHAR(255),
  timestamp TIMESTAMPTZ,
  data JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Embeddings (pgvector)
CREATE TABLE embeddings (
  embedding_id UUID PRIMARY KEY,
  event_id UUID REFERENCES episodic_memory(event_id),
  content_hash VARCHAR(64),
  vector vector(1536),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_embeddings_vector ON embeddings USING ivfflat (vector vector_cosine_ops);

-- Governance & Escalations
CREATE TABLE escalations (
  escalation_id UUID PRIMARY KEY,
  task_id VARCHAR(255),
  created_at TIMESTAMPTZ,
  status VARCHAR(50),
  approver_email VARCHAR(255),
  approved_at TIMESTAMPTZ,
  reason TEXT
);

-- Audit trail
CREATE TABLE audit_log (
  audit_id UUID PRIMARY KEY,
  timestamp TIMESTAMPTZ,
  task_id VARCHAR(255),
  action VARCHAR(255),
  details JSONB,
  correlation_id VARCHAR(255)
);
```

### Neo4j Graph Schema

```cypher
-- Semantic entities
CREATE (:Entity {id: "", name: "", type: ""})

-- Relationships
CREATE (e1:Entity)-[:RELATES_TO]->(e2:Entity)

-- Queries
MATCH (e:Entity)-[:RELATES_TO]->(:Entity)
RETURN e.name
```

### Redis Keys

```
task:{task_id}                    # Task cache
memory:context:{task_id}          # Context cache
escalation:pending:{id}           # Pending escalations
metrics:task:submitted            # Metrics counters
```

---

## Monitoring & Observability

### Prometheus Metrics

```
# Task execution
emma_tasks_submitted_total{type="research"} 42
emma_tasks_completed_total{type="research", status="success"} 40
emma_tasks_duration_seconds{type="research", le=1.0} 35

# Memory operations
emma_memory_store_duration_seconds{operation="write", le=0.1} 100
emma_memory_search_duration_seconds{operation="similarity", le=0.5} 95

# Database connections
emma_db_connections_active 8
emma_db_connection_pool_size 10
emma_db_query_duration_seconds{query="store_event", le=0.1} 80

# Cache operations
emma_cache_hits_total 1000
emma_cache_misses_total 100
```

### Structured Logs

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "logger": "emma_agent.controller",
  "message": "Task completed",
  "task_id": "task_abc123",
  "task_type": "research",
  "status": "completed",
  "duration_ms": 1234,
  "correlation_id": "corr_xyz789",
  "user_id": "user@company.com"
}
```

---

## Testing Guide

### Run All Tests

```bash
pytest tests/ -v --cov=emma_agent --cov-report=html
```

### Run Specific Test Module

```bash
pytest tests/test_controller.py -v
pytest tests/test_memory.py -v
pytest tests/test_governance.py -v
```

### Run with Coverage Report

```bash
pytest tests/ --cov=emma_agent --cov-report=term-missing
```

### Run Integration Tests Only

```bash
pytest tests/ -m integration -v
```

### Mock External Services

```python
# In test fixtures (conftest.py)
@pytest.fixture
def mock_openai():
    with patch("openai.Embedding.create") as mock:
        mock.return_value = MockEmbedding(...)
        yield mock
```

---

## Deployment Checklist

- [ ] Clone repository
- [ ] Create .env file with secrets
- [ ] Initialize databases (PostgreSQL, Redis, Neo4j)
- [ ] Run migrations: `python -m alembic upgrade head`
- [ ] Run tests: `pytest tests/ -v --cov`
- [ ] Build Docker image: `docker build -t emma:1.0.0 .`
- [ ] Deploy with docker-compose or Kubernetes
- [ ] Verify health: `curl http://localhost:8000/health`
- [ ] Check metrics: `curl http://localhost:9000/metrics`
- [ ] Set up monitoring (Prometheus, Grafana)
- [ ] Configure logging (ELK, Datadog, etc.)
- [ ] Enable alerts for escalations

---

## Support Resources

- **GitHub**: https://github.com/l9/emma_agent
- **Documentation**: https://docs.emma.l9.ai
- **Issues**: https://github.com/l9/emma_agent/issues
- **Slack**: #emma-agent-support
- **Email**: emma-team@l9.ai

---

**Generated:** December 14, 2025, 1:04 AM EST  
**Module Version:** 1.0.0  
**Status:** ✅ Production Ready  
**All Quality Gates:** ✅ Passed
