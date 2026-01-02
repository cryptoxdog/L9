"""
Email Agent Configuration
=========================

Centralized configuration for Gmail agent paths and settings.
"""

import os
from pathlib import Path

# Base data root
GMAIL_DATA_ROOT = Path(os.path.expanduser("~/.l9/gmail"))

# File paths
TOKENS_FILE = GMAIL_DATA_ROOT / "tokens.json"
CLIENT_SECRET_FILE = GMAIL_DATA_ROOT / "client_secret.json"
ATTACHMENTS_DIR = GMAIL_DATA_ROOT / "attachments"

# Gmail account
GMAIL_ACCOUNT = "nc@scrapmanagement.com"

# Gmail API scopes
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send",
]


def ensure_dirs():
    """
    Ensure all required directories exist.
    Creates directories if they don't exist.
    """
    GMAIL_DATA_ROOT.mkdir(parents=True, exist_ok=True)
    ATTACHMENTS_DIR.mkdir(parents=True, exist_ok=True)
    return {
        "gmail_data_root": str(GMAIL_DATA_ROOT),
        "tokens_file": str(TOKENS_FILE),
        "client_secret_file": str(CLIENT_SECRET_FILE),
        "attachments_dir": str(ATTACHMENTS_DIR),
    }
