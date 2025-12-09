"""
L9 Runtime Tests
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from l9_runtime.loop import L9RuntimeLoop
from l9_runtime.module_loader import ModuleLoader
from l9_runtime.event_bus import EventBus


def test_runtime_loop_initialization():
    """Test runtime loop initialization."""
    loop = L9RuntimeLoop()
    loop.initialize()
    
    assert loop.initialized == True
    assert len(loop.modules) > 0
    
    print(f"✅ Runtime loop initialization test passed: {len(loop.modules)} modules")


def test_runtime_dispatch():
    """Test runtime dispatch."""
    loop = L9RuntimeLoop()
    loop.initialize()
    
    # Test with utils module
    result = loop.dispatch({
        "command": "util_metric",
        "metric": "test_metric",
        "value": 1.0
    })
    
    assert isinstance(result, dict)
    assert "success" in result
    
    print(f"✅ Runtime dispatch test passed: {result.get('success')}")


def test_event_bus():
    """Test event bus."""
    bus = EventBus()
    bus.initialize()
    
    # Subscribe to event
    events_received = []
    
    def listener(data):
        events_received.append(data)
    
    bus.subscribe("test_event", listener)
    
    # Emit event
    bus.emit("test_event", {"test": "data"})
    
    assert len(events_received) == 1
    assert events_received[0]["test"] == "data"
    
    print("✅ Event bus test passed")


def test_module_loader():
    """Test module loader."""
    loader = ModuleLoader()
    modules = loader.discover_modules()
    
    assert len(modules) >= 7, f"Expected at least 7 modules, got {len(modules)}"
    
    print(f"✅ Module loader test passed: {len(modules)} modules")


if __name__ == "__main__":
    print("=== L9 Runtime Tests ===\n")
    
    test_runtime_loop_initialization()
    test_runtime_dispatch()
    test_event_bus()
    test_module_loader()
    
    print("\n=== ALL RUNTIME TESTS PASSED ===")

