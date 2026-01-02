# l/memory/shared/sanitizer.py

import re

SENSITIVE_PATTERNS = [
    r"sk-.*",  # API keys
    r"-----BEGIN PRIVATE KEY-----",  # PEM private keys
    r"password",  # general password key
    r"secret",  # general secret key
]


def sanitize(obj: dict):
    for key, value in list(obj.items()):
        for patt in SENSITIVE_PATTERNS:
            if isinstance(value, str) and re.search(patt, value, re.IGNORECASE):
                obj[key] = "[REDACTED]"
    return obj
