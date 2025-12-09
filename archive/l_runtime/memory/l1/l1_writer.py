# l/memory/l1/l1_writer.py

from l.memory.shared.supabase_client import get_supabase
from l.memory.shared.hashing import hash_payload

class L1Writer:
    def __init__(self):
        self.sb = get_supabase()

    def write_directive(self, payload: dict):
        payload["checksum"] = hash_payload(payload)
        return self.sb.table("l_directives").insert(payload).execute()

    def write_reasoning(self, payload: dict):
        return self.sb.table("l_reasoning_patterns").insert(payload).execute()

    def write_evaluation(self, payload: dict):
        return self.sb.table("l_evaluations").insert(payload).execute()

    def write_decision(self, payload: dict):
        return self.sb.table("l_decision_register").insert(payload).execute()

    def write_trace(self, payload: dict):
        return self.sb.table("l_execution_trace").insert(payload).execute()

    def write_buffer(self, payload: dict):
        return self.sb.table("l_memory_buffer").insert(payload).execute()

    def write_drift(self, payload: dict):
        return self.sb.table("l_drift_monitor").insert(payload).execute()

    def write_autonomy_change(self, payload: dict):
        return self.sb.table("l_autonomy_history").insert(payload).execute()

writer = L1Writer()

