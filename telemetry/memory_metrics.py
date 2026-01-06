"""
L9 Telemetry - Memory Metrics
=============================

Prometheus metrics for L9 memory substrate observability.
Tracks memory writes, searches, tool invocations, and latencies.

These metrics integrate with the L9 /metrics endpoint via
the prometheus_client library.

Version: 1.0.0
Author: L9 Enterprise

Usage:
    from telemetry.memory_metrics import (
        record_memory_write,
        record_memory_search,
        record_tool_invocation,
    )

    # After memory write:
    record_memory_write(segment="tool_audit", status="ok")

    # After memory search:
    record_memory_search(segment="session_context", hit_count=5)

    # After tool invocation:
    record_tool_invocation(tool_id="memory_search", status="success", duration_ms=42)
"""

from __future__ import annotations

import structlog
from typing import Optional

logger = structlog.get_logger(__name__)

# Try to import prometheus_client, gracefully degrade if not available
try:
    from prometheus_client import Counter, Histogram, Gauge, REGISTRY

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger.warning("prometheus_client not installed - metrics disabled")


# =============================================================================
# Metric Definitions
# =============================================================================

if PROMETHEUS_AVAILABLE:
    # Memory write metrics
    MEMORY_WRITE_TOTAL = Counter(
        "l9_memory_write_total",
        "Total number of memory write operations",
        ["segment", "status"],
    )

    MEMORY_WRITE_DURATION = Histogram(
        "l9_memory_write_duration_seconds",
        "Duration of memory write operations in seconds",
        ["segment"],
        buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    )

    # Memory search metrics
    MEMORY_SEARCH_TOTAL = Counter(
        "l9_memory_search_total",
        "Total number of memory search operations",
        ["segment", "search_type"],
    )

    MEMORY_SEARCH_HITS = Histogram(
        "l9_memory_search_hits",
        "Number of hits returned by memory searches",
        ["segment"],
        buckets=(0, 1, 2, 5, 10, 20, 50, 100),
    )

    # Tool invocation metrics
    TOOL_INVOCATION_TOTAL = Counter(
        "l9_tool_invocation_total",
        "Total number of tool invocations",
        ["tool_id", "status"],
    )

    TOOL_INVOCATION_DURATION = Histogram(
        "l9_tool_invocation_duration_ms",
        "Duration of tool invocations in milliseconds",
        ["tool_id"],
        buckets=(1, 5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000),
    )

    # Memory substrate health
    MEMORY_SUBSTRATE_HEALTHY = Gauge(
        "l9_memory_substrate_healthy",
        "Whether the memory substrate is healthy (1=healthy, 0=unhealthy)",
    )

    # Current packet store size (updated periodically)
    PACKET_STORE_SIZE = Gauge(
        "l9_packet_store_size",
        "Current number of packets in packet_store",
        ["segment"],
    )


# =============================================================================
# Recording Functions
# =============================================================================


def record_memory_write(
    segment: str,
    status: str = "ok",
    duration_seconds: Optional[float] = None,
) -> None:
    """
    Record a memory write operation.

    Args:
        segment: Memory segment (governance_meta, project_history, tool_audit, session_context)
        status: Write status (ok, partial, error)
        duration_seconds: Optional write duration in seconds
    """
    if not PROMETHEUS_AVAILABLE:
        return

    try:
        MEMORY_WRITE_TOTAL.labels(segment=segment, status=status).inc()
        if duration_seconds is not None:
            MEMORY_WRITE_DURATION.labels(segment=segment).observe(duration_seconds)
    except Exception as e:
        logger.warning("Failed to record memory write metric", error=str(e))


def record_memory_search(
    segment: str,
    hit_count: int = 0,
    search_type: str = "semantic",
) -> None:
    """
    Record a memory search operation.

    Args:
        segment: Memory segment searched
        hit_count: Number of results returned
        search_type: Type of search (semantic, exact, hybrid)
    """
    if not PROMETHEUS_AVAILABLE:
        return

    try:
        MEMORY_SEARCH_TOTAL.labels(segment=segment, search_type=search_type).inc()
        MEMORY_SEARCH_HITS.labels(segment=segment).observe(hit_count)
    except Exception as e:
        logger.warning("Failed to record memory search metric", error=str(e))


def record_tool_invocation(
    tool_id: str,
    status: str,
    duration_ms: int = 0,
) -> None:
    """
    Record a tool invocation.

    Args:
        tool_id: Canonical tool identifier
        status: Invocation status (success, failure, denied, timeout)
        duration_ms: Execution duration in milliseconds
    """
    if not PROMETHEUS_AVAILABLE:
        return

    try:
        TOOL_INVOCATION_TOTAL.labels(tool_id=tool_id, status=status).inc()
        TOOL_INVOCATION_DURATION.labels(tool_id=tool_id).observe(duration_ms)
    except Exception as e:
        logger.warning("Failed to record tool invocation metric", error=str(e))


def set_memory_substrate_health(healthy: bool) -> None:
    """
    Set the memory substrate health gauge.

    Args:
        healthy: Whether the memory substrate is healthy
    """
    if not PROMETHEUS_AVAILABLE:
        return

    try:
        MEMORY_SUBSTRATE_HEALTHY.set(1 if healthy else 0)
    except Exception as e:
        logger.warning("Failed to set memory substrate health", error=str(e))


def update_packet_store_size(segment: str, count: int) -> None:
    """
    Update the packet store size gauge for a segment.

    Args:
        segment: Memory segment
        count: Current packet count
    """
    if not PROMETHEUS_AVAILABLE:
        return

    try:
        PACKET_STORE_SIZE.labels(segment=segment).set(count)
    except Exception as e:
        logger.warning("Failed to update packet store size", error=str(e))


# =============================================================================
# Initialization
# =============================================================================


def init_metrics() -> bool:
    """
    Initialize memory metrics.

    Returns:
        True if metrics are available, False otherwise
    """
    if not PROMETHEUS_AVAILABLE:
        logger.warning("Prometheus metrics not available - install prometheus_client")
        return False

    # Set initial substrate health to healthy
    set_memory_substrate_health(True)

    logger.info("Memory metrics initialized")
    return True


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "PROMETHEUS_AVAILABLE",
    "record_memory_write",
    "record_memory_search",
    "record_tool_invocation",
    "set_memory_substrate_health",
    "update_packet_store_size",
    "init_metrics",
]



