Here are the **Phase-3 test files** and the **Cursor execution plan** to create and run them.

---

## 1️⃣ `tests/runtime/test_ws_protocol_static.py`

```python
"""
L9 Tests - WebSocket Protocol Static Tests
Version: 1.0.0

Covers:
- EventMessage default behavior
- AgentHeartbeat schema constraints
- ErrorEvent structure
"""

from uuid import UUID

import pytest

from core.schemas.ws_event_stream import (
    EventMessage,
    EventType,
    AgentHeartbeat,
    ErrorEvent,
)


class TestEventMessageBasics:
    def test_minimal_event_defaults(self):
        event = EventMessage(
            type=EventType.TASK_RESULT,
            agent_id="agent-1",
            payload={"task_id": "abc123", "result": "ok"},
        )

        assert isinstance(event.id, UUID)
        assert event.type == EventType.TASK_RESULT
        assert event.channel == "agent"
        assert event.agent_id == "agent-1"
        assert isinstance(event.timestamp, type(event.timestamp))
        assert isinstance(event.payload, dict)
        assert event.payload["task_id"] == "abc123"

    def test_handshake_event_roundtrip(self):
        event = EventMessage(
            type=EventType.HANDSHAKE,
            agent_id="mac_agent_01",
            payload={
                "capabilities": ["shell", "browser"],
                "version": "1.0.0",
            },
        )

        data = event.model_dump(mode="json")
        restored = EventMessage(**data)

        assert restored.type == EventType.HANDSHAKE
        assert restored.agent_id == "mac_agent_01"
        assert restored.payload["capabilities"] == ["shell", "browser"]
        assert restored.payload["version"] == "1.0.0"


class TestAgentHeartbeat:
    def test_heartbeat_defaults_and_constraints(self):
        hb = AgentHeartbeat(agent_id="mac_agent_01")

        assert hb.agent_id == "mac_agent_01"
        assert hb.running_tasks == 0
        assert hb.load_avg is None
        assert hb.memory_usage_mb is None
        assert hb.cpu_percent is None

    def test_heartbeat_with_metrics(self):
        hb = AgentHeartbeat(
            agent_id="mac_agent_01",
            load_avg=0.5,
            running_tasks=3,
            memory_usage_mb=512.0,
            cpu_percent=42.0,
        )

        assert hb.load_avg == 0.5
        assert hb.running_tasks == 3
        assert hb.memory_usage_mb == 512.0
        assert hb.cpu_percent == 42.0


class TestErrorEvent:
    def test_error_event_basic(self):
        err = ErrorEvent(
            agent_id="mac_agent_01",
            code="AUTH_FAILED",
            message="Invalid token",
            details={"reason": "token_mismatch"},
        )

        data = err.model_dump(mode="json")
        restored = ErrorEvent(**data)

        assert restored.code == "AUTH_FAILED"
        assert restored.message == "Invalid token"
        assert restored.details["reason"] == "token_mismatch"
        assert restored.agent_id == "mac_agent_01"
```

---

## 2️⃣ `tests/runtime/test_websocket_orchestrator_basic.py`

```python
"""
L9 Tests - WebSocketOrchestrator Basic Behavior
Version: 1.0.0

Covers:
- register / unregister
- is_connected
- send_to_agent
- broadcast
"""

import asyncio

import pytest

from core.schemas.ws_event_stream import EventMessage, EventType
from runtime.websocket_orchestrator import WebSocketOrchestrator


class FakeWebSocket:
    def __init__(self):
        self.sent = []
        self.accepted = False
        self.closed = False

    async def accept(self):
        self.accepted = True

    async def send_json(self, data):
        self.sent.append(data)

    async def close(self, code: int = 1000):
        self.closed = True
        self.close_code = code


@pytest.mark.asyncio
class TestWebSocketOrchestratorBasic:
    async def test_register_and_is_connected(self):
        orch = WebSocketOrchestrator()
        ws = FakeWebSocket()

        await orch.register("agent-1", ws, metadata={"role": "mac"})

        assert await orch.is_connected("agent-1") is True
        agents = await orch.get_connected_agents()
        assert "agent-1" in agents

        meta = await orch.get_agent_metadata("agent-1")
        assert meta["role"] == "mac"

    async def test_send_to_agent_and_unregistered_error(self):
        orch = WebSocketOrchestrator()
        ws = FakeWebSocket()
        await orch.register("agent-1", ws)

        event = EventMessage(
            type=EventType.TASK_ASSIGNED,
            agent_id="agent-1",
            payload={"task_id": "t-1"},
        )

        await orch.send_to_agent("agent-1", event)

        assert len(ws.sent) == 1
        frame = ws.sent[0]
        assert frame["type"] == EventType.TASK_ASSIGNED
        assert frame["payload"]["task_id"] == "t-1"

        # Unregistered agent should raise
        with pytest.raises(RuntimeError):
            await orch.send_to_agent("agent-2", event)

    async def test_broadcast_exclude(self):
        orch = WebSocketOrchestrator()
        ws1 = FakeWebSocket()
        ws2 = FakeWebSocket()
        ws3 = FakeWebSocket()

        await orch.register("a1", ws1)
        await orch.register("a2", ws2)
        await orch.register("a3", ws3)

        event = EventMessage(
            type=EventType.LOG,
            payload={"msg": "hello"},
        )

        count = await orch.broadcast(event, exclude={"a2"})

        assert count == 2
        assert len(ws1.sent) == 1
        assert len(ws2.sent) == 0
        assert len(ws3.sent) == 1

    async def test_unregister_clears_state(self):
        orch = WebSocketOrchestrator()
        ws = FakeWebSocket()
        await orch.register("agent-1", ws)

        await orch.unregister("agent-1")
        assert await orch.is_connected("agent-1") is False
        assert await orch.get_agent_metadata("agent-1") is None
```

---

## 3️⃣ `tests/orchestrator/test_ws_task_router_routing.py`

```python
"""
L9 Tests - WS Task Router Routing
Version: 1.0.0

Covers:
- TASK_RESULT routing → TaskEnvelope
- ERROR routing → TaskEnvelope
- HEARTBEAT → None (no task)
"""

from uuid import uuid4

from core.schemas.ws_event_stream import EventMessage, EventType
from core.schemas.tasks import TaskEnvelope, TaskKind
from orchestration.ws_task_router import route_event_to_task, RouterConfig


class TestWSTaskRouterRouting:
    def test_task_result_routing(self):
        event = EventMessage(
            type=EventType.TASK_RESULT,
            agent_id="mac_agent_01",
            payload={
                "task_id": "t-123",
                "result": {"status": "ok"},
                "status": "completed",
                "extra": "meta",
            },
        )

        cfg = RouterConfig(emit_packets=True, trace_events=True, default_priority=3)
        envelope = route_event_to_task(event, cfg)

        assert isinstance(envelope, TaskEnvelope)
        assert envelope.agent_id == "mac_agent_01"
        assert envelope.source_event_id == event.id

        task = envelope.task
        assert task.kind == TaskKind.RESULT.value
        assert task.priority == 3
        assert task.trace_id == event.trace_id
        assert task.payload["original_task_id"] == "t-123"
        assert task.payload["result"]["status"] == "ok"
        assert task.payload["status"] == "completed"
        assert task.payload["extra"] == "meta"

    def test_error_event_routing(self):
        event = EventMessage(
            type=EventType.ERROR,
            agent_id="mac_agent_01",
            payload={
                "code": "AUTH_FAILED",
                "message": "bad token",
                "details": {"reason": "mismatch"},
                "recoverable": False,
            },
        )

        cfg = RouterConfig()
        envelope = route_event_to_task(event, cfg)

        assert isinstance(envelope, TaskEnvelope)
        assert envelope.agent_id == "mac_agent_01"

        task = envelope.task
        assert task.kind == TaskKind.ERROR.value
        assert task.payload["error_code"] == "AUTH_FAILED"
        assert task.payload["message"] == "bad token"
        assert task.payload["details"]["reason"] == "mismatch"
        assert task.payload["recoverable"] is False

    def test_heartbeat_does_not_generate_task(self):
        event = EventMessage(
            type=EventType.HEARTBEAT,
            agent_id="mac_agent_01",
            payload={"running_tasks": 3},
        )

        cfg = RouterConfig()
        envelope = route_event_to_task(event, cfg)

        assert envelope is None
```

---

## 4️⃣ `tests/world_model/test_world_model_repository_basic.py`

```python
"""
L9 Tests - WorldModelRepository Basic Behavior
Version: 1.0.0

Covers:
- upsert_entity uses get_pool() and fetchrow()
- delete_entity uses execute() and returns bool
- list_entities uses fetch()
"""

import asyncio
from uuid import uuid4

import pytest

from world_model.repository import WorldModelRepository, get_pool


class FakeConnection:
    def __init__(self):
        self.fetchrow_calls = []
        self.fetch_calls = []
        self.execute_calls = []

    async def fetchrow(self, query: str, *args):
        self.fetchrow_calls.append((query, args))
        # Minimal fake row structure: dict-like with expected keys
        return {
            "entity_id": args[0] if args else "e-1",
            "entity_type": "test",
            "attributes": {"name": "Test"},
            "confidence": 1.0,
            "updated_at": "2025-01-01T00:00:00Z",
        }

    async def fetch(self, query: str, *args):
        self.fetch_calls.append((query, args))
        return [
            {
                "entity_id": "e-1",
                "entity_type": "test",
                "attributes": {"name": "One"},
                "confidence": 0.9,
                "updated_at": "2025-01-01T00:00:00Z",
            }
        ]

    async def execute(self, query: str, *args):
        self.execute_calls.append((query, args))
        return "DELETE 1"

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class FakePool:
    def __init__(self):
        self.conn = FakeConnection()
        self.acquire_calls = 0

    async def acquire(self):
        self.acquire_calls += 1
        return self.conn

    async def close(self):
        pass


@pytest.mark.asyncio
class TestWorldModelRepositoryBasic:
    async def test_upsert_entity_uses_pool_and_fetchrow(self, monkeypatch):
        fake_pool = FakePool()

        async def fake_get_pool():
            return fake_pool

        monkeypatch.setattr("world_model.repository.get_pool", fake_get_pool)

        repo = WorldModelRepository()
        row = await repo.upsert_entity(
            entity_id="entity-123",
            attributes={"name": "Test"},
            entity_type="test_type",
            confidence=0.8,
        )

        assert fake_pool.acquire_calls == 1
        assert fake_pool.conn.fetchrow_calls, "fetchrow should be called"
        assert row["entity_id"] == "entity-123"

    async def test_delete_entity_returns_bool(self, monkeypatch):
        fake_pool = FakePool()

        async def fake_get_pool():
            return fake_pool

        monkeypatch.setattr("world_model.repository.get_pool", fake_get_pool)

        repo = WorldModelRepository()
        deleted = await repo.delete_entity("entity-999")

        assert isinstance(deleted, bool)
        assert deleted is True
        assert fake_pool.conn.execute_calls, "execute should be called"

    async def test_list_entities_uses_fetch(self, monkeypatch):
        fake_pool = FakePool()

        async def fake_get_pool():
            return fake_pool

        monkeypatch.setattr("world_model.repository.get_pool", fake_get_pool)

        repo = WorldModelRepository()
        rows = await repo.list_entities(limit=10)

        assert isinstance(rows, list)
        assert len(rows) == 1
        assert fake_pool.conn.fetch_calls, "fetch should be called"
```

---
