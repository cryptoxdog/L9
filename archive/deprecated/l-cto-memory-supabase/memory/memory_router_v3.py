# l/memory/memory_router_v4.py

import time
from typing import Dict, Any
from l_cto.memory.shared.supabase_client import get_supabase
from l_cto.memory.shared.hashing import hash_payload
from l_cto.memory.shared.constants import L1_TABLES, MAC_TABLES, META_TABLES
from l_cto.memory.shared.governance_filter import governance_filter
from l_cto.memory.shared.concurrency_manager import concurrency
from l_cto.memory.l1.l1_query import query as l1_query


class MemoryRouterV3:
    """
    Multi-tier memory router:
      - L1 (L's personal cognition/logs)
      - MAC (multi-agent / coordination)
      - META (Board / Constellation)

    Tier selection rules:
      - If table ∈ L1_TABLES → L1 route
      - If table ∈ MAC_TABLES → MAC route
      - If table ∈ META_TABLES → META route
      - Else: reject (invalid schema)
    """

    def __init__(self):
        self.sb = get_supabase()

    # -----------------------------
    # Core routing
    # -----------------------------
    def write(self, table: str, payload: Dict[str, Any]) -> Dict:
        # Governance validation
        validation = governance_filter.validate(payload)
        if not validation["allowed"]:
            return {"success": False, "error": validation["reason"]}

        tier = self._resolve_tier(table)
        self._apply_enrichment(payload, tier)

        # Concurrency protection
        with concurrency.lock(table):
            return self.sb.table(table).insert(payload).execute()

    def read(self, table: str, filters: Dict[str, Any] = None) -> Dict:
        tier = self._resolve_tier(table)
        q = self.sb.table(table).select("*")
        if filters:
            q = q.match(filters)
        return q.execute()

    def delete(self, table: str, filters: Dict[str, Any]) -> Dict:
        tier = self._resolve_tier(table)
        q = self.sb.table(table).delete().match(filters)
        return q.execute()

    def query(self, table: str, **filters):
        """Query passthrough to L1 query layer."""
        return l1_query.filter(table, **filters)

    # -----------------------------
    # Helpers
    # -----------------------------
    def _resolve_tier(self, table: str) -> str:
        if table in L1_TABLES:
            return "L1"
        if table in MAC_TABLES:
            return "MAC"
        if table in META_TABLES:
            return "META"
        raise ValueError(
            f"Invalid table '{table}' — not part of L1/MAC/META memory schema."
        )

    def _apply_enrichment(self, payload: Dict[str, Any], tier: str):
        payload["__tier"] = tier
        payload["__router_version"] = "3.0"
        payload["__checksum"] = hash_payload(payload)
        payload["__ingest_ts"] = time.time()


router = MemoryRouterV3()
