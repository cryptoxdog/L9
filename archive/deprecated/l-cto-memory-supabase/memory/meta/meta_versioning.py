# l/memory/meta/meta_versioning.py

from l_cto.memory.shared.supabase_client import get_supabase
import json
import hashlib


class MemoryVersioning:
    def __init__(self):
        self.sb = get_supabase()

    def snapshot_schema(self, schema: dict):
        checksum = hashlib.sha256(json.dumps(schema).encode()).hexdigest()
        return (
            self.sb.table("meta_invariants")
            .insert(
                {
                    "invariant_name": "schema_snapshot",
                    "invariant_value": schema,
                    "version": checksum,
                }
            )
            .execute()
        )


versioner = MemoryVersioning()
