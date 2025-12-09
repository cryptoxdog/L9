"""Tests for ops monitoring modules without optional dependencies."""

import logging
from datetime import datetime

import pytest

from ops.monitoring import real_time_dashboard, alerting_system


@pytest.mark.asyncio
async def test_metrics_collector_context_manager_without_aiohttp(monkeypatch, caplog):
    """MetricsCollector should not attempt HTTP when aiohttp is missing."""
    monkeypatch.setattr(real_time_dashboard, "aiohttp", None, raising=False)

    collector = real_time_dashboard.MetricsCollector()

    with caplog.at_level(logging.WARNING):
        async with collector as active:
            assert active.session is None

    assert any("aiohttp is not installed" in record.getMessage() for record in caplog.records)


@pytest.mark.asyncio
async def test_alert_router_skips_webhook_without_aiohttp(monkeypatch, caplog):
    """AlertRouter should log and skip webhook delivery when aiohttp is absent."""
    monkeypatch.setattr(alerting_system, "aiohttp", None, raising=False)

    router = alerting_system.AlertRouter(config_path="/tmp/alerts")
    alert = alerting_system.Alert(
        alert_id="alert-1",
        timestamp=datetime.now(),
        severity=alerting_system.AlertSeverity.CRITICAL,
        component="pipeline_orchestrator",
        metric="latency",
        message="Test alert",
        current_value=1.2,
        threshold_value=0.5
    )

    with caplog.at_level(logging.WARNING):
        await router._send_webhook_alert(alert, ["http://example.com/webhook"])

    assert any(
        "aiohttp is not installed" in record.getMessage()
        for record in caplog.records
    )

