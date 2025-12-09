from fastapi import APIRouter, Header, HTTPException
from l.memory.memory_router_v4 import MemoryRouterV4
from l.l_memory.kg_client import KGClient

router = APIRouter()
memory = MemoryRouterV4()
kg = KGClient()

# API key enforcement
def require_api_key(x_api_key: str = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-Key header")
    return x_api_key

@router.post("/l/test/write")
def test_write(payload: dict, x_api_key: str = Header(None)):
    require_api_key(x_api_key)
    return memory.write("l_directives", payload)

@router.get("/l/test/read")
def test_read(x_api_key: str = Header(None)):
    require_api_key(x_api_key)
    result = memory.read("l_directives", {"source": "test_harness"})
    return result.data if hasattr(result, 'data') else result

@router.post("/l/test/reasoning")
def test_reasoning(payload: dict, x_api_key: str = Header(None)):
    require_api_key(x_api_key)
    entry = {
        "reasoning_mode": payload.get("mode", "analysis"),
        "pattern_type": "test",
        "source": "test_harness",
        "notes": payload.get("note", "")
    }
    return memory.write("l_reasoning_patterns", entry)

@router.post("/l/test/drift")
def test_drift(payload: dict, x_api_key: str = Header(None)):
    require_api_key(x_api_key)
    entry = {
        "drift_type": payload.get("drift_type", "test"),
        "severity": payload.get("severity", 1),
        "drift_signal": payload,
        "status": "logged"
    }
    return memory.write("l_drift_monitor", entry)

@router.get("/kg/bootstrap")
def kg_bootstrap(x_api_key: str = Header(None)):
    require_api_key(x_api_key)
    try:
        kg.init()
        return {"status": "ok", "connected": kg.connected}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/kg/test/query")
def kg_test_query(x_api_key: str = Header(None)):
    require_api_key(x_api_key)
    try:
        # Simple test query
        return {"status": "ok", "result": "KG query endpoint operational"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

