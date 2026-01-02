# l/memory/l1/l1_validators.py

from typing import Dict

FORBIDDEN_KEYS = {"system_password", "private_key", "api_secret"}


def sanitize_payload(payload: Dict) -> Dict:
    """Hard filter that strips dangerous or forbidden keys."""
    return {k: v for k, v in payload.items() if k not in FORBIDDEN_KEYS}


def validate_payload(payload: Dict):
    """Reject payloads that violate safety constraints."""
    for key in payload:
        if key in FORBIDDEN_KEYS:
            raise ValueError(f"Forbidden key in payload: {key}")

    if not isinstance(payload, dict):
        raise ValueError("Payload must be a dictionary")

    return True
