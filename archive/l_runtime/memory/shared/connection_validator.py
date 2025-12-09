# l/memory/shared/connection_validator.py

import os
from l.memory.shared.supabase_client import get_supabase

class SupabaseConnectionValidator:
    def __init__(self):
        self.sb = get_supabase()

    def validate_env(self):
        required = ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"]
        missing = [x for x in required if not os.getenv(x)]
        return {"missing_env": missing}

    def validate_tables(self):
        tables = [
            "l_directives", "l_reasoning_patterns", "l_evaluations",
            "l_decision_register", "l_execution_trace", "l_memory_buffer",
            "l_drift_monitor", "l_autonomy_history",
            "mac_agent_registry", "mac_message_bus", "mac_task_delegations",
            "mac_coordination_graph", "mac_constellation_links",
            "meta_constitution", "meta_invariants", "meta_incident_log",
            "meta_audit_log", "meta_ontology"
        ]
        result = {}
        for t in tables:
            try:
                q = self.sb.table(t).select("id").limit(1).execute()
                result[t] = "ok" if q else "error"
            except Exception:
                result[t] = "missing"
        return result

validator = SupabaseConnectionValidator()

