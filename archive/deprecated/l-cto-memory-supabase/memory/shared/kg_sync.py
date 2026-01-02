# l/memory/shared/kg_sync.py

from l_cto.memory.l1.l1_reader import reader
from l_cto.memory.shared.supabase_client import get_supabase


class KGSync:
    def __init__(self):
        self.sb = get_supabase()

    def sync_decisions_to_neo4j(self):
        decisions = reader.get_decisions(limit=50).data
        # push via REST → your Neo4j endpoint
        # (neo4j connector to be added)
        return decisions


sync = KGSync()
