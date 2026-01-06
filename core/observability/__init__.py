"""
L9 Observability Module - Production-ready auto-tracing and metrics.

This module provides:
- Distributed tracing with W3C Trace Context standard
- Automatic instrumentation via decorators
- Failure detection and recovery
- Context window management strategies
- Multi-backend span export (console, file, substrate, Datadog, Honeycomb)
- SRE metrics and agent KPIs
- Sampling and cardinality management

Quick start:

    from core.observability.service import initialize_observability
    from core.observability.l9_integration import (
        instrument_agent_executor,
        instrument_tool_registry,
        instrument_governance_engine,
        instrument_memory_substrate,
    )

    # Initialize at app startup
    observability = await initialize_observability(substrate_service=substrate_svc)

    # Instrument L9 services (one-time)
    await instrument_agent_executor(executor_service)
    await instrument_tool_registry(tool_registry)
    await instrument_governance_engine(governance_engine)
    await instrument_memory_substrate(substrate_service)

    # All subsequent calls are automatically traced!
"""

from .config import ObservabilitySettings, load_config
from .models import (
    TraceContext,
    Span,
    LLMGenerationSpan,
    ToolCallSpan,
    ContextAssemblySpan,
    RAGRetrievalSpan,
    GovernanceCheckSpan,
    AgentTrajectorySpan,
    FailureSignal,
    RemediationAction,
    SREMetric,
    AgentKPI,
    SpanKind,
    SpanStatus,
    FailureClass,
)
from .instrumentation import (
    trace_span,
    trace_llm_call,
    trace_tool_call,
    trace_governance_check,
)
from .service import ObservabilityService, initialize_observability
from .exporters import (
    SpanExporter,
    AsyncSpanExporter,
    ConsoleExporter,
    JSONFileExporter,
    SubstrateExporter,
    CompositeExporter,
)
from .aggregation import (
    MetricsAggregator,
    KPITracker,
)
from .context_strategies import (
    ContextStrategy,
    NaiveTruncationStrategy,
    RecencyBiasedWindowStrategy,
    HierarchicalSummarizationStrategy,
    RAGStrategy,
    HybridStrategy,
    AdaptiveStrategySelector,
)
from .failures import (
    FailureDetector,
    RecoveryExecutor,
    RecoveryAction,
    get_recovery_actions,
)
from .l9_integration import (
    instrument_agent_executor,
    instrument_tool_registry,
    instrument_governance_engine,
    instrument_memory_substrate,
    instrument_aios_runtime,
)

__version__ = "1.0.0"
__all__ = [
    # Config
    "ObservabilitySettings",
    "load_config",
    # Models
    "TraceContext",
    "Span",
    "LLMGenerationSpan",
    "ToolCallSpan",
    "ContextAssemblySpan",
    "RAGRetrievalSpan",
    "GovernanceCheckSpan",
    "AgentTrajectorySpan",
    "FailureSignal",
    "RemediationAction",
    "SREMetric",
    "AgentKPI",
    "SpanKind",
    "SpanStatus",
    "FailureClass",
    # Instrumentation
    "trace_span",
    "trace_llm_call",
    "trace_tool_call",
    "trace_governance_check",
    # Service
    "ObservabilityService",
    "initialize_observability",
    # Exporters
    "SpanExporter",
    "AsyncSpanExporter",
    "ConsoleExporter",
    "JSONFileExporter",
    "SubstrateExporter",
    "CompositeExporter",
    # Aggregation
    "MetricsAggregator",
    "KPITracker",
    # Context Strategies
    "ContextStrategy",
    "NaiveTruncationStrategy",
    "RecencyBiasedWindowStrategy",
    "HierarchicalSummarizationStrategy",
    "RAGStrategy",
    "HybridStrategy",
    "AdaptiveStrategySelector",
    # Failures & Recovery
    "FailureDetector",
    "RecoveryExecutor",
    "RecoveryAction",
    "get_recovery_actions",
    # L9 Integration
    "instrument_agent_executor",
    "instrument_tool_registry",
    "instrument_governance_engine",
    "instrument_memory_substrate",
    "instrument_aios_runtime",
]
