# l/memory/mac/mac_router.py

from l_cto.memory.shared.supabase_client import get_supabase
from l_cto.memory.shared.constants import MAC_TABLES


class MACRouter:
    """Router for MAC (Multi-Agent Coordination) memory layer."""

    def __init__(self):
        self.sb = get_supabase()

    def write(self, table: str, payload: dict):
        if table not in MAC_TABLES:
            raise ValueError(f"Table {table} not in MAC schema")
        return self.sb.table(table).insert(payload).execute()

    def read(self, table: str, filters: dict = None):
        if table not in MAC_TABLES:
            raise ValueError(f"Table {table} not in MAC schema")
        q = self.sb.table(table).select("*")
        if filters:
            q = q.match(filters)
        return q.execute()

    def log_message(self, payload: dict):
        """Convenience method for logging MAC messages."""
        return self.write("mac_message_bus", payload)


router = MACRouter()
