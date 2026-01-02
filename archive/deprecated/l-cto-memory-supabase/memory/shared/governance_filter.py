# l/memory/shared/governance_filter.py

import json
from typing import Dict, Any

FORBIDDEN_KEYS = {
    "password",
    "api_key",
    "secret",
    "token",
    "private_key",
    "credential",
    "auth",
}

MAX_PAYLOAD_SIZE = 25000  # 25KB limit


class GovernanceFilter:
    """Validates payloads before writing to memory."""

    def validate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate payload against governance rules.

        Returns:
            {"allowed": bool, "reason": str}
        """
        # Check for forbidden keys
        for key in payload.keys():
            if any(forbidden in key.lower() for forbidden in FORBIDDEN_KEYS):
                return {"allowed": False, "reason": f"Forbidden key detected: {key}"}

        # Check payload size
        try:
            payload_size = len(json.dumps(payload))
            if payload_size > MAX_PAYLOAD_SIZE:
                return {
                    "allowed": False,
                    "reason": f"Payload too large: {payload_size} bytes (max: {MAX_PAYLOAD_SIZE})",
                }
        except Exception as e:
            return {
                "allowed": False,
                "reason": f"Payload serialization failed: {str(e)}",
            }

        # All checks passed
        return {"allowed": True, "reason": "passed"}


governance_filter = GovernanceFilter()
