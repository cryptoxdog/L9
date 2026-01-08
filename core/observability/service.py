"""
Main observability service orchestration.

Manages span export, metrics computation, failure detection, and service lifecycle.
"""

import asyncio
import structlog
from typing import List, Optional, Dict, Any
from datetime import datetime
from collections import defaultdict

from .config import ObservabilitySettings, load_config
from .models import Span, TraceContext, FailureSignal, FailureClass

logger = structlog.get_logger(__name__)


class ObservabilityService:
    """Main service for observability subsystem."""

    _instance: Optional["ObservabilityService"] = None
    _lock = asyncio.Lock()

    def __init__(
        self,
        config: Optional[ObservabilitySettings] = None,
        substrate_service: Optional[Any] = None,
    ):
        """Initialize observability service."""
        self.config = config or load_config()
        self.substrate_service = substrate_service
        self.spans: List[Span] = []
        self.failures: List[FailureSignal] = []
        self.exporters: List[Any] = []
        self._trace_context: Optional[TraceContext] = None
        self._setup_logging()
        logger.info("ObservabilityService initialized", extra={
            "sampling_rate": self.config.sampling_rate,
            "exporters": self.config.exporters,
        })

    def _setup_logging(self) -> None:
        """Configure logging."""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(self.config.log_level)

    @classmethod
    def get(cls) -> Optional["ObservabilityService"]:
        """Get global instance."""
        return cls._instance

    @classmethod
    def set_global(cls, service: "ObservabilityService") -> None:
        """Set global instance."""
        cls._instance = service

    async def initialize_exporters(self) -> None:
        """Initialize configured exporters."""
        from .exporters import (
            ConsoleExporter, JSONFileExporter, SubstrateExporter,
        )

        for exporter_name in self.config.exporters:
            try:
                if exporter_name == "console":
                    self.exporters.append(ConsoleExporter())
                elif exporter_name == "file":
                    self.exporters.append(JSONFileExporter(self.config.file_export_path))
                elif exporter_name == "substrate":
                    if self.substrate_service and self.config.substrate_enabled:
                        self.exporters.append(SubstrateExporter(self.substrate_service))
                # datadog, honeycomb etc. would go here in extended implementation
                else:
                    logger.warning(f"Unknown exporter: {exporter_name}")
            except Exception as exc:
                logger.error(f"Failed to initialize exporter {exporter_name}: {exc}")

    def current_trace_context(self) -> TraceContext:
        """Get current trace context (create if needed)."""
        if not self._trace_context:
            self._trace_context = TraceContext()
        return self._trace_context

    def set_trace_context(self, ctx: TraceContext) -> None:
        """Set trace context (e.g., from incoming request headers)."""
        self._trace_context = ctx

    def export_span(self, span: Span) -> None:
        """Export a span to all configured exporters."""
        if not self.config.enabled:
            return

        # Apply sampling decision
        ctx = self.current_trace_context()
        if span.status == SpanStatus.ERROR:
            sample = self.config.error_sampling_rate >= 1.0
        else:
            sample = ctx.is_sampled

        if not sample:
            return

        # Store locally
        self.spans.append(span)

        # Export via all backends (async, non-blocking)
        for exporter in self.exporters:
            try:
                if hasattr(exporter, "export_async"):
                    asyncio.create_task(exporter.export_async([span]))
                else:
                    exporter.export([span])
            except Exception as exc:
                logger.error(f"Export failed: {exc}")

    async def compute_metrics(self) -> Dict[str, Any]:
        """Compute SRE metrics from recent spans."""
        if not self.spans:
            return {
                "span_count": 0,
                "error_count": 0,
                "error_rate": 0.0,
                "p95_latency_ms": 0,
                "p99_latency_ms": 0,
            }

        durations = [s.duration_ms for s in self.spans if s.duration_ms]
        errors = [s for s in self.spans if s.status.value == "ERROR"]

        durations.sort()
        p95_idx = max(0, int(len(durations) * 0.95) - 1)
        p99_idx = max(0, int(len(durations) * 0.99) - 1)

        return {
            "span_count": len(self.spans),
            "error_count": len(errors),
            "error_rate": len(errors) / len(self.spans) if self.spans else 0.0,
            "p95_latency_ms": durations[p95_idx] if p95_idx < len(durations) else 0,
            "p99_latency_ms": durations[p99_idx] if p99_idx < len(durations) else 0,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def detect_failures(self) -> List[FailureSignal]:
        """Detect failures from recent spans."""
        signals = []

        for span in self.spans:
            # Tool timeout
            if (
                span.name.startswith("tool.")
                and span.duration_ms
                and span.duration_ms > 30000
            ):
                signals.append(FailureSignal(
                    failure_class=FailureClass.TOOL_TIMEOUT,
                    span_id=span.span_id,
                    trace_id=span.trace_id,
                    context={"tool": span.name, "duration_ms": span.duration_ms},
                ))

            # Tool error
            if span.name.startswith("tool.") and span.status.value == "ERROR":
                signals.append(FailureSignal(
                    failure_class=FailureClass.TOOL_ERROR,
                    span_id=span.span_id,
                    trace_id=span.trace_id,
                    context={"tool": span.name, "error": span.error},
                ))

            # Governance denial
            if (
                span.name.startswith("governance.")
                and hasattr(span, "policy_result")
                and span.policy_result == "deny"
            ):
                signals.append(FailureSignal(
                    failure_class=FailureClass.GOVERNANCE_DENIED,
                    span_id=span.span_id,
                    trace_id=span.trace_id,
                    context={"policy": span.name},
                ))

            # Context overflow
            if (
                hasattr(span, "overflow_event")
                and span.overflow_event
            ):
                signals.append(FailureSignal(
                    failure_class=FailureClass.CONTEXT_WINDOW_EXCEEDED,
                    span_id=span.span_id,
                    trace_id=span.trace_id,
                    context={"tokens_used": span.attributes.get("tokens_used")},
                ))

        self.failures.extend(signals)
        return signals

    async def shutdown(self) -> None:
        """Graceful shutdown."""
        logger.info("ObservabilityService shutting down...")
        # Flush remaining spans
        for exporter in self.exporters:
            try:
                if hasattr(exporter, "flush"):
                    await exporter.flush()
            except Exception as exc:
                logger.error(f"Flush failed: {exc}")
        logger.info("ObservabilityService shutdown complete")


async def initialize_observability(
    config: Optional[ObservabilitySettings] = None,
    substrate_service: Optional[Any] = None,
) -> ObservabilityService:
    """
    Initialize and return global observability service.
    
    Call this once at application startup.
    """
    if ObservabilityService.get() is not None:
        return ObservabilityService.get()

    config = config or load_config()
    service = ObservabilityService(config=config, substrate_service=substrate_service)
    await service.initialize_exporters()
    ObservabilityService.set_global(service)
    return service


def get_observability_service() -> Optional[ObservabilityService]:
    """
    Get the global observability service instance.

    Returns None if observability hasn't been initialized.
    This is the preferred way to access the service from other modules.
    """
    return ObservabilityService.get()


# Import SpanStatus for export_span
from .models import SpanStatus
