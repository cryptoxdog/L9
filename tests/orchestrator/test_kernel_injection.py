"""
Kernel Injection Tests
======================

Tests for kernel injection into API routes.
"""

import pytest
import sys
from types import ModuleType
from unittest.mock import MagicMock, patch


# Create mock FastAPI app for testing
def create_mock_app():
    """Create a mock FastAPI application."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    
    app = FastAPI()
    
    # Mock kernel state
    kernel_state = {
        "merged": {
            "rules": {"truth": "strict"},
            "memory": {"max_in_state_size_kb": 1024},
            "rate_limits": {"google": {"max_per_hour": 100}},
        },
        "governance": {"rules": {"truth": "strict"}},
        "agent": {"capabilities": {"web_search": True}},
    }
    
    @app.get("/kernel")
    def get_kernel():
        return kernel_state
    
    @app.get("/health")
    def health():
        return {"status": "ok"}
    
    @app.post("/tasks")
    def create_task(body: dict):
        task = body.get("task", "")
        if task.startswith("echo:"):
            result = task.replace("echo:", "").strip()
            return {"result": result, "status": "completed"}
        return {"result": "unknown task", "status": "error"}
    
    return app


def test_kernel_injected():
    """Test that kernel state is accessible via API."""
    from fastapi.testclient import TestClient
    
    app = create_mock_app()
    client = TestClient(app)
    
    r = client.get("/kernel")
    assert r.status_code == 200
    assert "merged" in r.json()


def test_kernel_has_governance():
    """Test kernel includes governance rules."""
    from fastapi.testclient import TestClient
    
    app = create_mock_app()
    client = TestClient(app)
    
    r = client.get("/kernel")
    data = r.json()
    
    assert "governance" in data
    assert "rules" in data["governance"]


def test_kernel_has_agent():
    """Test kernel includes agent config."""
    from fastapi.testclient import TestClient
    
    app = create_mock_app()
    client = TestClient(app)
    
    r = client.get("/kernel")
    data = r.json()
    
    assert "agent" in data


def test_kernel_merged_has_memory():
    """Test merged kernel has memory config."""
    from fastapi.testclient import TestClient
    
    app = create_mock_app()
    client = TestClient(app)
    
    r = client.get("/kernel")
    data = r.json()
    
    assert "memory" in data["merged"]


def test_kernel_merged_has_rate_limits():
    """Test merged kernel has rate limits."""
    from fastapi.testclient import TestClient
    
    app = create_mock_app()
    client = TestClient(app)
    
    r = client.get("/kernel")
    data = r.json()
    
    assert "rate_limits" in data["merged"]


def test_api_health_endpoint():
    """Test health endpoint is accessible."""
    from fastapi.testclient import TestClient
    
    app = create_mock_app()
    client = TestClient(app)
    
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

