"""
Memory Telemetry - Prometheus metrics, structured logging, observability
========================================================================
"""

import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class MemoryTelemetry:
    """
    Observability for memory operations.
    
    Metrics:
    - memory_write_total: Total packets written
    - memory_search_total: Total searches performed
    - memory_cache_hits_total: Total cache hits
    - memory_search_duration_ms: Search latency
    - memory_packet_count: Current packet gauge
    """
    
    def __init__(self):
        self.logger = logger
        self.write_total = 0
        self.search_total = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self._init_prometheus()
    
    def _init_prometheus(self):
        """Initialize Prometheus metrics if available."""
        try:
            from prometheus_client import Counter, Histogram, Gauge
            
            self.write_counter = Counter(
                "memory_write_total",
                "Total memory packets written",
                ["segment", "agent_id"]
            )
            
            self.search_counter = Counter(
                "memory_search_total",
                "Total memory searches",
                ["segment", "agent_id"]
            )
            
            self.cache_hits_counter = Counter(
                "memory_cache_hits_total",
                "Total cache hits",
                ["segment"]
            )
            
            self.search_duration = Histogram(
                "memory_search_duration_ms",
                "Memory search duration milliseconds",
                buckets=[10, 50, 100, 500, 1000, 5000, 10000]
            )
            
            self.packet_count = Gauge(
                "memory_packet_count",
                "Current packet count",
                ["segment", "agent_id"]
            )
        
        except ImportError:
            self.logger.warning("Prometheus not available; metrics disabled")
            self.write_counter = None
            self.search_counter = None
            self.cache_hits_counter = None
            self.search_duration = None
            self.packet_count = None
    
    def log_write(self, segment: str, agent_id: str):
        """Record write operation."""
        self.write_total += 1
        if self.write_counter:
            self.write_counter.labels(segment=segment, agent_id=agent_id).inc()
        
        self.log_structured(
            "memory_write",
            segment=segment,
            agent_id=agent_id
        )
    
    def log_search(self, segment: str, agent_id: str, result_count: int, duration_ms: float):
        """Record search operation."""
        self.search_total += 1
        if self.search_counter:
            self.search_counter.labels(segment=segment, agent_id=agent_id).inc()
        if self.search_duration:
            self.search_duration.observe(duration_ms)
        
        self.log_structured(
            "memory_search",
            segment=segment,
            agent_id=agent_id,
            results=result_count,
            duration_ms=duration_ms
        )
    
    def log_cache_hit(self, segment: str):
        """Record cache hit."""
        self.cache_hits += 1
        if self.cache_hits_counter:
            self.cache_hits_counter.labels(segment=segment).inc()
    
    def log_cache_miss(self, segment: str):
        """Record cache miss."""
        self.cache_misses += 1
    
    def log_structured(
        self,
        event: str,
        level: str = "INFO",
        **kwargs
    ) -> None:
        """
        Structured JSON logging.
        
        Example:
            telemetry.log_structured(
                "memory_write",
                chunk_id="abc123",
                segment="project_history",
                agent_id="L"
            )
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            "level": level,
            **kwargs
        }
        
        # Log as JSON for aggregation
        getattr(self.logger, level.lower())(str(log_entry))
    
    def get_stats(self) -> dict:
        """Get telemetry statistics."""
        return {
            "write_total": self.write_total,
            "search_total": self.search_total,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": (
                self.cache_hits / (self.cache_hits + self.cache_misses)
                if (self.cache_hits + self.cache_misses) > 0 else 0
            )
        }


# Global telemetry instance
_telemetry = None


def get_telemetry() -> MemoryTelemetry:
    """Get or create global telemetry instance."""
    global _telemetry
    if _telemetry is None:
        _telemetry = MemoryTelemetry()
    return _telemetry

# ============================================================================
# L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT
# ============================================================================
__dora_block__ = {
    "component_id": "TOO-OPER-010",
    "component_name": "Telemetry",
    "module_version": "1.0.0",
    "created_at": "2026-01-08T03:15:14Z",
    "created_by": "L9_DORA_Injector",
    "layer": "operations",
    "domain": "tools",
    "type": "utility",
    "status": "active",
    "governance_level": "medium",
    "compliance_required": True,
    "audit_trail": True,
    "purpose": "Implements MemoryTelemetry for telemetry functionality",
    "dependencies": [],
}

# ============================================================================
# END L9 DORA BLOCK
# ============================================================================
