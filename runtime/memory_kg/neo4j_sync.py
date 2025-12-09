"""
Streaming sync from Supabase → Neo4j

Triggered hourly, or manually by L.
"""

from l.memory.shared.supabase_client import get_supabase
from l.l_memory.kg_client import KGClient

def sync_supabase_to_neo4j():
    sb = get_supabase()
    kg = KGClient()
    kg.init()
    
    tables = ["l_directives", "l_execution_trace", "mac_message_bus"]
    
    for table in tables:
        res = sb.table(table).select("*").execute()
        for row in res.data:
            kg.upsert(table.replace("_", "").title(), row)
    
    return {"success": True}

