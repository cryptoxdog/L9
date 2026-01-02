"""
Task Execution Tests
====================

Tests for basic task execution via API.
"""


def create_task_app():
    """Create a mock FastAPI app with task endpoint."""
    from fastapi import FastAPI

    app = FastAPI()

    @app.post("/tasks")
    def create_task(body: dict):
        task = body.get("task", "")

        # Echo task
        if task.startswith("echo:"):
            result = task.replace("echo:", "").strip()
            return {"result": result, "status": "completed"}

        # Add task
        if task.startswith("add:"):
            try:
                parts = task.replace("add:", "").strip().split("+")
                result = sum(int(p.strip()) for p in parts)
                return {"result": str(result), "status": "completed"}
            except Exception:
                return {"result": "error", "status": "failed"}

        return {"result": "unknown task type", "status": "error"}

    @app.get("/tasks/{task_id}")
    def get_task(task_id: str):
        return {"task_id": task_id, "status": "completed"}

    return app


def test_basic_task_execution():
    """Test basic echo task execution."""
    from fastapi.testclient import TestClient

    app = create_task_app()
    client = TestClient(app)

    r = client.post("/tasks", json={"task": "echo: hello"})
    assert r.status_code == 200
    assert "hello" in r.json()["result"]


def test_task_returns_result():
    """Test task execution returns result field."""
    from fastapi.testclient import TestClient

    app = create_task_app()
    client = TestClient(app)

    r = client.post("/tasks", json={"task": "echo: test"})
    data = r.json()

    assert "result" in data


def test_task_returns_status():
    """Test task execution returns status field."""
    from fastapi.testclient import TestClient

    app = create_task_app()
    client = TestClient(app)

    r = client.post("/tasks", json={"task": "echo: test"})
    data = r.json()

    assert "status" in data
    assert data["status"] == "completed"


def test_echo_task_content():
    """Test echo task returns correct content."""
    from fastapi.testclient import TestClient

    app = create_task_app()
    client = TestClient(app)

    messages = ["hello", "world", "test message", "123"]

    for msg in messages:
        r = client.post("/tasks", json={"task": f"echo: {msg}"})
        assert msg in r.json()["result"]


def test_unknown_task_type():
    """Test unknown task type returns error."""
    from fastapi.testclient import TestClient

    app = create_task_app()
    client = TestClient(app)

    r = client.post("/tasks", json={"task": "unknown: test"})
    data = r.json()

    assert data["status"] == "error"


def test_add_task():
    """Test add task execution."""
    from fastapi.testclient import TestClient

    app = create_task_app()
    client = TestClient(app)

    r = client.post("/tasks", json={"task": "add: 1 + 2 + 3"})
    data = r.json()

    assert data["status"] == "completed"
    assert "6" in data["result"]


def test_get_task_by_id():
    """Test retrieving task by ID."""
    from fastapi.testclient import TestClient

    app = create_task_app()
    client = TestClient(app)

    r = client.get("/tasks/test-123")
    assert r.status_code == 200
    assert r.json()["task_id"] == "test-123"
