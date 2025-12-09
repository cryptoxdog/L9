# l/memory/meta/meta_router.py

from l.memory.shared.supabase_client import get_supabase
from l.memory.shared.constants import META_TABLES

class METARouter:
    """Router for META (System Governance) memory layer."""
    
    def __init__(self):
        self.sb = get_supabase()
    
    def write(self, table: str, payload: dict):
        if table not in META_TABLES:
            raise ValueError(f"Table {table} not in META schema")
        return self.sb.table(table).insert(payload).execute()
    
    def read(self, table: str, filters: dict = None):
        if table not in META_TABLES:
            raise ValueError(f"Table {table} not in META schema")
        q = self.sb.table(table).select("*")
        if filters:
            q = q.match(filters)
        return q.execute()
    
    def audit(self, payload: dict):
        """Convenience method for logging audit events."""
        return self.write("meta_audit_log", payload)
    
    def incident(self, payload: dict):
        """Convenience method for logging incidents."""
        return self.write("meta_incident_log", payload)

router = METARouter()

