# l/memory/l1/l1_reader.py

from l_cto.memory.shared.supabase_client import get_supabase


class L1Reader:
    def __init__(self):
        self.sb = get_supabase()

    def get_recent_directives(self, limit=20):
        return (
            self.sb.table("l_directives")
            .select("*")
            .order("timestamp", desc=True)
            .limit(limit)
            .execute()
        )

    def get_recent_trace(self, limit=50):
        return (
            self.sb.table("l_execution_trace")
            .select("*")
            .order("timestamp", desc=True)
            .limit(limit)
            .execute()
        )

    def get_drift_events(self, severity_min=3):
        return (
            self.sb.table("l_drift_monitor")
            .select("*")
            .gte("severity", severity_min)
            .execute()
        )

    def get_decisions(self, limit=50):
        return (
            self.sb.table("l_decision_register")
            .select("*")
            .order("timestamp", desc=True)
            .limit(limit)
            .execute()
        )


reader = L1Reader()
