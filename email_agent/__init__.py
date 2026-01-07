"""L9 Email Agent - Gmail API integration."""

from email_agent.gmail_client import GmailClient
from email_agent.client import execute_email_task
from email_agent.triage import summarize_inbox, run_daily_digest
from email_agent.credentials import (
    load_client_secrets,
    create_flow,
    exchange_code_for_tokens,
    save_tokens,
    load_tokens,
)

__all__ = [
    "GmailClient",
    "execute_email_task",
    "summarize_inbox",
    "run_daily_digest",
    "load_client_secrets",
    "create_flow",
    "exchange_code_for_tokens",
    "save_tokens",
    "load_tokens",
]
