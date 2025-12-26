"""
L9 Core Governance - Approval Manager
======================================

Manages approval of high-risk tasks that require Igor's explicit approval.

Version: 1.0.0
"""

from __future__ import annotations

import structlog
from datetime import datetime
from typing import Optional

from memory.substrate_models import PacketEnvelopeIn

logger = structlog.get_logger(__name__)


class ApprovalManager:
    """Manages approval of high-risk tasks."""
    
    def __init__(self, substrate_service):
        """
        Initialize ApprovalManager.
        
        Args:
            substrate_service: Memory substrate service for storing approval records
        """
        self._substrate = substrate_service
    
    async def approve_task(self, task_id: str, approved_by: str, reason: Optional[str] = None) -> bool:
        """
        Approve a task. Only Igor can approve.
        
        Args:
            task_id: Task identifier
            approved_by: Approver identifier (must be "Igor")
            reason: Optional approval reason
            
        Returns:
            True if approved, False if unauthorized
        """
        if approved_by != "Igor":
            logger.warning(f"Unauthorized approval attempt by {approved_by}")
            return False
        
        await self._substrate.write_packet(
            packet_in=PacketEnvelopeIn(
                packet_type="approval_record",
                payload={
                    "task_id": task_id,
                    "approved_by": approved_by,
                    "timestamp": datetime.utcnow().isoformat(),
                    "reason": reason or "",
                }
            )
        )
        
        logger.info(f"Task {task_id} approved by Igor")
        return True
    
    async def reject_task(self, task_id: str, rejected_by: str, reason: str) -> bool:
        """
        Reject a task. Only Igor can reject.
        
        Args:
            task_id: Task identifier
            rejected_by: Rejector identifier (must be "Igor")
            reason: Rejection reason (required)
            
        Returns:
            True if rejected, False if unauthorized
        """
        if rejected_by != "Igor":
            logger.warning(f"Unauthorized rejection attempt by {rejected_by}")
            return False
        
        await self._substrate.write_packet(
            packet_in=PacketEnvelopeIn(
                packet_type="rejection_record",
                payload={
                    "task_id": task_id,
                    "rejected_by": rejected_by,
                    "timestamp": datetime.utcnow().isoformat(),
                    "reason": reason,
                }
            )
        )
        
        logger.info(f"Task {task_id} rejected by Igor")
        return True
    
    async def is_approved(self, task_id: str) -> bool:
        """
        Check if task is approved.
        
        Args:
            task_id: Task identifier
            
        Returns:
            True if approved, False otherwise
        """
        results = await self._substrate.search_packets_by_type(
            packet_type="approval_record",
            limit=100,
        )
        # Filter by task_id in payload
        for result in results:
            if result.get("payload", {}).get("task_id") == task_id:
                return True
        return False

