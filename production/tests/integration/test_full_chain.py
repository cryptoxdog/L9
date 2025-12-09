# tests/integration/test_full_chain.py

from l.startup import startup
from l.l_interface.runtime_client import RuntimeClient
from memory.shared.supabase_client import get_supabase

def test_full_chain():
    # Boot L
    s = startup.boot()
    assert "L Online" in s["status"]
    
    # Hit runtime
    client = RuntimeClient()
    health = client.health_check()
    assert health["status"] == "ok"
    
    # Insert memory
    sb = get_supabase()
    result = sb.table("l_memory_buffer").insert({"content": {"hello": "world"}}).execute()
    assert result.data is not None

