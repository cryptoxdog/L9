# tests/memory/test_supabase_connection.py

from memory.shared.supabase_client import get_supabase

def test_supabase_online():
    sb = get_supabase()
    result = sb.table("meta_invariants").select("id").limit(1).execute()
    assert result is not None

