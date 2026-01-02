"""
Memory Router v4 — DEPRECATED: Use MemorySubstrateService directly

This router is deprecated. All memory operations should use:
- memory.substrate_service.MemorySubstrateService
- memory.substrate_models.PacketEnvelopeIn

This file is kept for reference only and will be archived.
"""

import structlog
from typing import Dict, Any

logger = structlog.get_logger(__name__)

# DEPRECATED: This router is no longer used
# Use MemorySubstrateService.write_packet() instead


class MemoryRouterV4:
    """
    DEPRECATED: Use MemorySubstrateService directly.

    This router is kept for backward compatibility but should not be used.
    All new code should use:
        from memory.substrate_service import MemorySubstrateService
        from memory.substrate_models import PacketEnvelopeIn

        await substrate_service.write_packet(
            PacketEnvelopeIn(
                packet_type="...",
                payload={...},
                metadata=PacketMetadata(agent="l-cto")
            )
        )
    """

    def __init__(self):
        logger.warning(
            "MemoryRouterV4 is deprecated. Use MemorySubstrateService.write_packet() instead."
        )
        self._deprecated = True

    def write(self, table: str, payload: Dict[str, Any]) -> Dict:
        """DEPRECATED: Use MemorySubstrateService.write_packet() instead."""
        logger.warning(
            f"MemoryRouterV4.write() called for table={table}. "
            "This is deprecated. Migrate to MemorySubstrateService."
        )
        return {
            "success": False,
            "error": "MemoryRouterV4 is deprecated. Use MemorySubstrateService.write_packet()",
            "deprecated": True,
        }

    def read(self, table: str, filters: Dict = None):
        """DEPRECATED: Use MemorySubstrateService.search_packets_by_type() instead."""
        logger.warning(
            f"MemoryRouterV4.read() called for table={table}. "
            "This is deprecated. Migrate to MemorySubstrateService."
        )
        return {
            "success": False,
            "error": "MemoryRouterV4 is deprecated. Use MemorySubstrateService.search_packets_by_type()",
            "deprecated": True,
        }


# DEPRECATED: Do not use
router = MemoryRouterV4()
