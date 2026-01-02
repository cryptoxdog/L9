# l/memory/shared/schema_cache.py

from functools import lru_cache
from l_cto.memory.shared.supabase_client import get_supabase


@lru_cache(maxsize=1)
def get_schema_cache():
    sb = get_supabase()
    meta = sb.table("meta_ontology").select("*").execute()
    return {row["entity_type"]: row["schema"] for row in meta.data}
