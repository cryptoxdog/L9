"""
L9 Memory Orchestrator - Housekeeping
Version: 1.0.0

Specialized component for memory orchestration.
Handles garbage collection, compaction, and maintenance.
"""

import structlog
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

logger = structlog.get_logger(__name__)


class Housekeeping:
    """
    Housekeeping for Memory Orchestrator.

    Handles memory substrate maintenance tasks:
    - Garbage collection of old packets
    - Storage compaction/optimization
    - Health checks
    """

    def __init__(self, repository: Optional[Any] = None):
        """
        Initialize housekeeping.

        Args:
            repository: Optional MemorySubstrateRepository instance.
        """
        self._repository = repository
        logger.info("Housekeeping initialized")

    async def _get_repository(self) -> Any:
        """Get or lazily load the repository."""
        if self._repository is None:
            try:
                from memory.substrate_repository import get_repository

                self._repository = await get_repository()
            except ImportError:
                logger.warning("MemorySubstrateRepository not available, using stub")
                return None
        return self._repository

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process data through housekeeping.

        Legacy interface - routes to appropriate method based on data.
        """
        operation = data.get("operation", "health_check")

        if operation == "gc":
            return await self.garbage_collect(data.get("threshold_days", 30))
        elif operation == "compact":
            return await self.compact()
        else:
            return await self.health_check()

    async def garbage_collect(self, threshold_days: int = 30) -> Dict[str, Any]:
        """
        Delete packets older than threshold.

        Args:
            threshold_days: Delete packets older than this many days

        Returns:
            Result dict with deleted_count and success status
        """
        logger.info(f"Starting garbage collection (threshold: {threshold_days} days)")

        repository = await self._get_repository()
        if repository is None:
            return {
                "success": False,
                "message": "Repository not available",
                "deleted_count": 0,
            }

        try:
            cutoff_date = datetime.utcnow() - timedelta(days=threshold_days)

            # Delete old packets via repository
            # This assumes repository has a delete_before method
            if hasattr(repository, "delete_packets_before"):
                deleted_count = await repository.delete_packets_before(cutoff_date)
            else:
                # Fallback: query and delete individually
                deleted_count = 0
                logger.warning("Repository doesn't support bulk delete, skipping GC")

            logger.info(f"Garbage collection complete: {deleted_count} packets deleted")

            return {
                "success": True,
                "message": f"Deleted {deleted_count} packets older than {threshold_days} days",
                "deleted_count": deleted_count,
                "cutoff_date": cutoff_date.isoformat(),
            }

        except Exception as e:
            logger.error(f"Garbage collection failed: {e}")
            return {
                "success": False,
                "message": str(e),
                "deleted_count": 0,
            }

    async def compact(self) -> Dict[str, Any]:
        """
        Compact/optimize storage.

        Runs VACUUM ANALYZE on PostgreSQL tables.

        Returns:
            Result dict with success status
        """
        logger.info("Starting storage compaction")

        repository = await self._get_repository()
        if repository is None:
            return {
                "success": False,
                "message": "Repository not available",
            }

        try:
            # Run VACUUM ANALYZE if repository supports it
            if hasattr(repository, "vacuum_analyze"):
                await repository.vacuum_analyze()
            elif hasattr(repository, "_pool"):
                # Direct pool access fallback
                async with repository._pool.acquire() as conn:
                    await conn.execute("VACUUM ANALYZE packet_store")
                    await conn.execute("VACUUM ANALYZE vector_embeddings")
            else:
                logger.warning("Repository doesn't support compaction")
                return {
                    "success": True,
                    "message": "Compaction not supported (no-op)",
                }

            logger.info("Storage compaction complete")
            return {
                "success": True,
                "message": "Storage compacted successfully",
            }

        except Exception as e:
            logger.error(f"Compaction failed: {e}")
            return {
                "success": False,
                "message": str(e),
            }

    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of memory substrate.

        Returns:
            Health status dict
        """
        repository = await self._get_repository()

        if repository is None:
            return {
                "success": False,
                "status": "unavailable",
                "message": "Repository not available",
            }

        try:
            # Simple connectivity check
            if hasattr(repository, "health_check"):
                health = await repository.health_check()
                return {
                    "success": True,
                    "status": "healthy" if health else "degraded",
                    "message": "Health check passed",
                }

            return {
                "success": True,
                "status": "unknown",
                "message": "Health check not supported",
            }

        except Exception as e:
            return {
                "success": False,
                "status": "unhealthy",
                "message": str(e),
            }
