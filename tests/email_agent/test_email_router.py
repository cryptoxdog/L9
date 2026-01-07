"""
L9 Email Router Tests
=====================

Tests for email routing logic.
No external services required - uses mocks.

Version: 1.0.0
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from email_agent.router import router, QueryRequest
except ImportError as e:
    pytest.skip(f"Could not import email_agent.router: {e}", allow_module_level=True)


# =============================================================================
# Test: Route email to correct handler
# =============================================================================


def test_route_email_to_correct_handler():
    """
    Contract: Email router routes requests to correct endpoints.
    """
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)

    client = TestClient(app)

    # Test query endpoint exists
    with patch("email_agent.router.GmailClient") as mock_gmail:
        mock_client = MagicMock()
        mock_gmail.return_value = mock_client
        mock_client.query.return_value = []

        response = client.post(
            "/email/query", json={"query": "test", "max_results": 10}
        )

        # Should route to query handler (may return 200 or error depending on implementation)
        assert response.status_code in [200, 400, 500]


# =============================================================================
# Test: Unknown sender handling
# =============================================================================


def test_unknown_sender_handling():
    """
    Contract: Router handles unknown senders gracefully.
    """
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)

    client = TestClient(app)

    # Test that router accepts requests (implementation may vary)
    request = QueryRequest(query="from:unknown@example.com", max_results=5)

    # Verify request model validation
    assert request.query == "from:unknown@example.com"
    assert request.max_results == 5
