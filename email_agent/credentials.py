"""
Gmail OAuth Credentials Handler
Handles OAuth2 flow for Gmail API authentication.
Account: nc@scrapmanagement.com
"""

import json
import structlog
from typing import Optional, Dict, Any

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    GMAIL_AUTH_AVAILABLE = True
except ImportError:
    GMAIL_AUTH_AVAILABLE = False
    structlog.get_logger(__name__).warning("Gmail OAuth libraries not available")

from email_agent.config import TOKENS_FILE, CLIENT_SECRET_FILE, SCOPES, ensure_dirs

logger = structlog.get_logger(__name__)

# Ensure directories exist on import
ensure_dirs()


def load_client_secrets() -> Optional[Dict[str, Any]]:
    """
    Load OAuth client secrets from ~/.l9/gmail/client_secret.json

    Returns:
        Client secrets dictionary or None if not found
    """
    if not CLIENT_SECRET_FILE.exists():
        logger.error(f"Client secrets not found at {CLIENT_SECRET_FILE}")
        logger.info("Please download OAuth2 credentials from Google Cloud Console")
        logger.info("Save as: ~/.l9/gmail/client_secret.json")
        return None

    try:
        with open(CLIENT_SECRET_FILE, "r") as f:
            secrets = json.load(f)
        logger.info(f"Loaded client secrets from {CLIENT_SECRET_FILE}")
        return secrets
    except Exception as e:
        logger.error(f"Failed to load client secrets: {e}")
        return None


def create_flow(redirect_uri: Optional[str] = None) -> Optional[Any]:
    """
    Create OAuth2 flow for Gmail authentication.

    Args:
        redirect_uri: Optional redirect URI (defaults to localhost)

    Returns:
        InstalledAppFlow instance or None if client secrets not found
    """
    if not GMAIL_AUTH_AVAILABLE:
        logger.error("Gmail OAuth libraries not available")
        return None

    secrets = load_client_secrets()
    if not secrets:
        return None

    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(CLIENT_SECRET_FILE), SCOPES, redirect_uri=redirect_uri
        )
        return flow
    except Exception as e:
        logger.error(f"Failed to create OAuth flow: {e}")
        return None


def exchange_code_for_tokens(
    authorization_code: str, redirect_uri: str
) -> Optional[Credentials]:
    """
    Exchange authorization code for access/refresh tokens.

    Args:
        authorization_code: Authorization code from OAuth callback
        redirect_uri: Redirect URI used in OAuth flow

    Returns:
        Credentials object or None if exchange failed
    """
    if not GMAIL_AUTH_AVAILABLE:
        logger.error("Gmail OAuth libraries not available")
        return None

    try:
        flow = create_flow(redirect_uri=redirect_uri)
        if not flow:
            return None

        # Exchange code for tokens
        flow.fetch_token(code=authorization_code)
        credentials = flow.credentials

        # Save tokens
        save_tokens(credentials)

        logger.info("Successfully exchanged authorization code for tokens")
        return credentials
    except Exception as e:
        logger.error(f"Failed to exchange code for tokens: {e}")
        return None


def save_tokens(credentials: Credentials) -> bool:
    """
    Save OAuth tokens to ~/.l9/gmail/tokens.json

    Args:
        credentials: Credentials object with tokens

    Returns:
        True if saved successfully
    """
    if not GMAIL_AUTH_AVAILABLE:
        logger.error("Gmail OAuth libraries not available")
        return False

    try:
        token_data = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes,
        }

        with open(TOKENS_FILE, "w") as f:
            json.dump(token_data, f, indent=2)

        logger.info(f"Saved tokens to {TOKENS_FILE}")
        return True
    except Exception as e:
        logger.error(f"Failed to save tokens: {e}")
        return False


def load_tokens() -> Optional[Credentials]:
    """
    Load OAuth tokens from ~/.l9/gmail/tokens.json

    Returns:
        Credentials object or None if not found/invalid
    """
    if not GMAIL_AUTH_AVAILABLE:
        logger.error("Gmail OAuth libraries not available")
        return None

    if not TOKENS_FILE.exists():
        logger.info(f"No tokens found at {TOKENS_FILE}")
        return None

    try:
        with open(TOKENS_FILE, "r") as f:
            token_data = json.load(f)

        credentials = Credentials(
            token=token_data.get("token"),
            refresh_token=token_data.get("refresh_token"),
            token_uri=token_data.get(
                "token_uri", "https://oauth2.googleapis.com/token"
            ),
            client_id=token_data.get("client_id"),
            client_secret=token_data.get("client_secret"),
            scopes=token_data.get("scopes", SCOPES),
        )

        # Refresh if expired
        if credentials.expired and credentials.refresh_token:
            logger.info("Tokens expired, refreshing...")
            credentials.refresh(Request())
            save_tokens(credentials)

        logger.info(f"Loaded tokens from {TOKENS_FILE}")
        return credentials
    except Exception as e:
        logger.error(f"Failed to load tokens: {e}")
        return None
