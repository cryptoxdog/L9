# l/memory/shared/normalizer.py

import json
from typing import Any, Dict

def normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Ensures all memory writes are JSON-serializable, sanitized, and normalized."""
    try:
        json.dumps(payload)  # serialization check
        return payload
    except TypeError:
        normalized = {}
        for k, v in payload.items():
            if hasattr(v, "dict"):
                normalized[k] = v.dict()
            elif hasattr(v, "__dict__"):
                normalized[k] = v.__dict__
            else:
                normalized[k] = str(v)
        return normalized

