"""
L9 PacketEnvelope Upgrade Package
=================================

Implements phases 2-5 of the PacketEnvelope frontier upgrade:

- Phase 2: Observability (OpenTelemetry, Jaeger, Prometheus)
- Phase 3: Standardization (CloudEvents v1.0)
- Phase 4: Scalability (Batch ingestion, CQRS, Event Sourcing)
- Phase 5: Governance (TTL enforcement, GDPR, Compliance)

Usage:
    from upgrades.packet_envelope import PacketEnvelopeUpgradeEngine
    
    engine = PacketEnvelopeUpgradeEngine()
    await engine.activate_all_phases()
"""

from upgrades.packet_envelope.integration import (
    PacketEnvelopeUpgradeEngine,
    PacketEnvelopeAdapter,
    PacketEnvelopeUpgradePhase,
    UpgradeState,
    validate_deployment,
)

__all__ = [
    "PacketEnvelopeUpgradeEngine",
    "PacketEnvelopeAdapter",
    "PacketEnvelopeUpgradePhase",
    "UpgradeState",
    "validate_deployment",
]

