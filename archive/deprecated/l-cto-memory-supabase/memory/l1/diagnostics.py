# l/memory/l1/diagnostics.py

from l_cto.memory.shared.supabase_client import get_supabase


class MemoryDiagnostics:
    def __init__(self):
        self.sb = get_supabase()

    def table_counts(self):
        tables = [
            "l_directives",
            "l_reasoning_patterns",
            "l_evaluations",
            "l_decision_register",
            "l_execution_trace",
            "l_memory_buffer",
            "l_drift_monitor",
            "l_autonomy_history",
        ]
        results = {}
        for t in tables:
            q = self.sb.table(t).select("id").execute()
            results[t] = len(q.data)
        return results

    def recent_errors(self):
        return (
            self.sb.table("l_execution_trace")
            .select("*")
            .eq("error_flag", True)
            .order("timestamp", desc=True)
            .limit(20)
            .execute()
        )


diagnostics = MemoryDiagnostics()
