# l/memory/l1/l1_query.py

from l_cto.memory.shared.supabase_client import get_supabase
from typing import Dict, Any, Optional


class L1Query:
    """Advanced query layer for L1 memory tables."""

    def __init__(self):
        self.sb = get_supabase()

    def get_recent(self, table: str, limit: int = 10):
        """Get most recent records from a table."""
        return (
            self.sb.table(table)
            .select("*")
            .order("timestamp", desc=True)
            .limit(limit)
            .execute()
        )

    def filter(self, table: str, **filters):
        """
        Filter records by arbitrary criteria.

        Usage:
            query.filter("l_directives", source="user", priority=1)
        """
        q = self.sb.table(table).select("*")

        for key, value in filters.items():
            q = q.eq(key, value)

        return q.execute()

    def search(self, table: str, field: str, pattern: str):
        """Search for pattern in a specific field."""
        return self.sb.table(table).select("*").ilike(field, f"%{pattern}%").execute()

    def count(self, table: str, filters: Optional[Dict[str, Any]] = None):
        """Count records matching filters."""
        q = self.sb.table(table).select("id", count="exact")

        if filters:
            for key, value in filters.items():
                q = q.eq(key, value)

        result = q.execute()
        return result.count if hasattr(result, "count") else 0


query = L1Query()
