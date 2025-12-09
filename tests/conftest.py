"""
L9 OS Test Suite - Root Configuration
=====================================

Shared fixtures for all test modules.
No network access required - all mocks are local.
"""

import sys
from pathlib import Path

import pytest

# Add project root and tests directory to path
PROJECT_ROOT = Path(__file__).parent.parent
TESTS_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(TESTS_ROOT))

# Import mocks
from mocks.kernel_mocks import (
    KernelState,
    KernelViolationError,
    load_kernels,
    merge_dicts,
)
from mocks.memory_mocks import (
    MockMemoryAdapter,
    MockPostgresCursor,
)
from mocks.world_model_mocks import (
    MockWorldModel,
    get_wm_status,
)
from mocks.orchestrator_mocks import (
    MockRedis,
    MockToolRegistry,
)


# =============================================================================
# Kernel Fixtures
# =============================================================================

@pytest.fixture
def kernel_state() -> KernelState:
    """Provide a fresh kernel state."""
    return load_kernels()


@pytest.fixture
def governance_kernel() -> dict:
    """Provide governance kernel config."""
    return {
        "rules": {"truth": "strict", "safety": "maximum"},
        "memory": {"max_in_state_size_kb": 1024},
        "constraints": {"no_hallucination": True},
    }


@pytest.fixture
def agent_kernel() -> dict:
    """Provide agent kernel config."""
    return {
        "rules": {"truth": "loose", "adaptability": "high"},
        "capabilities": {"web_search": True},
    }


# =============================================================================
# Memory Fixtures (Sync)
# =============================================================================

@pytest.fixture
def memory_adapter() -> MockMemoryAdapter:
    """Provide a mock memory adapter."""
    return MockMemoryAdapter(
        max_vectors=25000,
        blob_threshold_kb=512,
    )


@pytest.fixture
def postgres_cursor() -> MockPostgresCursor:
    """Provide a mock PostgreSQL cursor."""
    return MockPostgresCursor()


@pytest.fixture
def adapter(memory_adapter) -> MockMemoryAdapter:
    """Alias for memory_adapter fixture."""
    return memory_adapter


# =============================================================================
# Memory Fixtures (Async)
# =============================================================================

@pytest.fixture
async def async_redis():
    """Async Redis mock with in-memory store."""
    class AsyncMockRedis:
        def __init__(self):
            self.store = {}  # Instance-level to prevent test pollution

        async def get(self, k):
            return self.store.get(k)

        async def set(self, k, v):
            self.store[k] = v

        async def incr(self, k):
            self.store[k] = self.store.get(k, 0) + 1
            return self.store[k]

    return AsyncMockRedis()


@pytest.fixture
def async_postgres_cursor():
    """Postgres cursor mock returning ivfflat index DDL."""
    class AsyncMockCursor:
        def __init__(self):
            self.q = None

        def execute(self, q):
            self.q = q

        def fetchone(self):
            return ["CREATE INDEX memory_vectors_idx ON memory USING ivfflat"]

    return AsyncMockCursor()


@pytest.fixture
async def async_memory_adapter():
    """Async memory adapter with blob storage and packet management."""
    class AsyncMockMemory:
        def __init__(self):
            self.blobs = {}    # Instance-level
            self.packets = {}  # Instance-level
            self.idx = 0       # Instance-level

        async def store_blob(self, content):
            k = f"blob-{len(self.blobs)}"
            self.blobs[k] = content
            return k

        async def ingest(self, data):
            self.idx += 1
            pid = f"p{self.idx}"
            self.packets[pid] = data
            return {"packet_id": pid, **data}

        async def retrieve(self, pid):
            return self.packets.get(pid)

        async def run_pruning(self):
            # Simulate pruning to 20000 vectors
            return {"active_vectors": 20000}

    return AsyncMockMemory()


# =============================================================================
# World Model Fixtures
# =============================================================================

@pytest.fixture
def world_model() -> MockWorldModel:
    """Provide a mock world model."""
    return MockWorldModel()


@pytest.fixture
async def async_world_model():
    """Async world model mock with node/edge graph operations."""
    class AsyncMockWM:
        def __init__(self):
            self.nodes = {}  # Instance-level
            self.edges = []  # Instance-level

        async def create_node(self, t, data):
            nid = len(self.nodes)
            self.nodes[nid] = {"type": t, **data}
            return nid

        async def get_node(self, nid):
            return self.nodes.get(nid)

        async def link(self, a, b, rel):
            self.edges.append((a, b, rel))

        async def get_edges(self, nid):
            return [
                {"type": rel, "src": a, "dst": b}
                for (a, b, rel) in self.edges if a == nid
            ]

    return AsyncMockWM()


# =============================================================================
# Orchestrator Fixtures
# =============================================================================

@pytest.fixture
def redis() -> MockRedis:
    """Provide a mock Redis client."""
    return MockRedis()


@pytest.fixture
def tool_registry(redis) -> MockToolRegistry:
    """Provide a mock tool registry."""
    registry = MockToolRegistry(redis=redis)
    
    # Register some default tools
    registry.register_tool("echo", lambda x: x, rate_limit=1000)
    registry.register_tool("google", lambda q: {"results": []}, rate_limit=100)
    registry.register_tool("openai", lambda p: {"completion": ""}, rate_limit=500)
    
    return registry


# =============================================================================
# Async Support
# =============================================================================

@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# =============================================================================
# Test Data Fixtures
# =============================================================================

@pytest.fixture
def sample_packet() -> dict:
    """Provide a sample packet for testing."""
    return {
        "content": "Test content for packet",
        "metadata": {"source": "test"},
        "tags": ["test", "sample"],
    }


@pytest.fixture
def large_content() -> str:
    """Provide large content for blob testing."""
    return "x" * (2 * 1024 * 1024)  # 2MB


@pytest.fixture
def sample_checkpoint() -> dict:
    """Provide a sample checkpoint for testing."""
    return {
        "step": 3,
        "plan": [1, 2, 3],
        "state": {"key": "value"},
    }
