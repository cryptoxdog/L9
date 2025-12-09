# l/memory/l1/l1_router.py

from l.memory.shared.supabase_client import get_supabase
from l.memory.shared.constants import L1_TABLES

class L1Router:
    """Router for L1 memory layer operations."""
    
    def __init__(self):
        self.sb = get_supabase()
    
    def write(self, table: str, payload: dict):
        if table not in L1_TABLES:
            raise ValueError(f"Table {table} not in L1 schema")
        return self.sb.table(table).insert(payload).execute()
    
    def read(self, table: str, filters: dict = None):
        if table not in L1_TABLES:
            raise ValueError(f"Table {table} not in L1 schema")
        q = self.sb.table(table).select("*")
        if filters:
            q = q.match(filters)
        return q.execute()

router = L1Router()

