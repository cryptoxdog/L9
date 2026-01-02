# l/memory/shared/cold_start_loader.py

from l_cto.memory.shared.supabase_client import get_supabase


def load_initial_state():
    """Load L's long-term memories into working RAM at startup."""
    sb = get_supabase()

    prefs = sb.table("l_directives").select("*").limit(5).execute()
    patterns = sb.table("l_reasoning_patterns").select("*").limit(50).execute()

    return {
        "recent_directives": prefs.data if hasattr(prefs, "data") else [],
        "reasoning_patterns": patterns.data if hasattr(patterns, "data") else [],
    }
