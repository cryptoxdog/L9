# l/memory/shared/hashing.py

import hashlib
import json


def hash_payload(payload: dict) -> str:
    """Generate deterministic hash for any payload."""
    serialized = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()
