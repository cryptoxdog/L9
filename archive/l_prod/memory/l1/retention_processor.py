# l/memory/l1/retention_processor.py

from l.memory.shared.supabase_client import get_supabase
from datetime import datetime, timedelta

class RetentionProcessor:
    def __init__(self):
        self.sb = get_supabase()

    def run(self):
        cutoff = datetime.utcnow() - timedelta(days=7)
        return (
            self.sb.table("l_memory_buffer")
            .delete()
            .lt("timestamp", cutoff.isoformat())
            .execute()
        )

processor = RetentionProcessor()

