"""
L9 Core Governance - Approval Manager
======================================

Manages approval of high-risk tasks that require Igor's explicit approval.
Now includes governance pattern creation for closed-loop learning.

Version: 1.1.0
"""

from __future__ import annotations

import structlog
from datetime import datetime
from typing import Any, Dict, Optional

from memory.substrate_models import PacketEnvelopeIn
from memory.governance_patterns import (
    DecisionType,
    GovernancePattern,
    extract_conditions_from_reason,
)

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

    async def approve_task(
        self,
        task_id: str,
        approved_by: str,
        reason: Optional[str] = None,
        tool_name: Optional[str] = None,
        task_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Approve a task. Only Igor can approve.

        Also creates a governance pattern for closed-loop learning.

        Args:
            task_id: Task identifier
            approved_by: Approver identifier (must be "Igor")
            reason: Optional approval reason
            tool_name: Tool being approved (for pattern creation)
            task_type: Type of task (for pattern creation)
            context: Additional context (files, summary, etc.)

        Returns:
            True if approved, False if unauthorized
        """
        if approved_by != "Igor":
            logger.warning(f"Unauthorized approval attempt by {approved_by}")
            return False

        # Write approval record
        await self._substrate.write_packet(
            packet_in=PacketEnvelopeIn(
                packet_type="approval_record",
                payload={
                    "task_id": task_id,
                    "approved_by": approved_by,
                    "timestamp": datetime.utcnow().isoformat(),
                    "reason": reason or "",
                },
            )
        )

        # Create governance pattern for learning
        await self._write_governance_pattern(
            task_id=task_id,
            decision=DecisionType.APPROVED,
            reason=reason or "",
            tool_name=tool_name or "unknown",
            task_type=task_type or "general",
            context=context or {},
        )

        logger.info(f"Task {task_id} approved by Igor")
        return True

    async def reject_task(
        self,
        task_id: str,
        rejected_by: str,
        reason: str,
        tool_name: Optional[str] = None,
        task_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Reject a task. Only Igor can reject.

        Also creates a governance pattern for closed-loop learning.

        Args:
            task_id: Task identifier
            rejected_by: Rejector identifier (must be "Igor")
            reason: Rejection reason (required)
            tool_name: Tool being rejected (for pattern creation)
            task_type: Type of task (for pattern creation)
            context: Additional context (files, summary, etc.)

        Returns:
            True if rejected, False if unauthorized
        """
        if rejected_by != "Igor":
            logger.warning(f"Unauthorized rejection attempt by {rejected_by}")
            return False

        # Write rejection record
        await self._substrate.write_packet(
            packet_in=PacketEnvelopeIn(
                packet_type="rejection_record",
                payload={
                    "task_id": task_id,
                    "rejected_by": rejected_by,
                    "timestamp": datetime.utcnow().isoformat(),
                    "reason": reason,
                },
            )
        )

        # Create governance pattern for learning
        await self._write_governance_pattern(
            task_id=task_id,
            decision=DecisionType.REJECTED,
            reason=reason,
            tool_name=tool_name or "unknown",
            task_type=task_type or "general",
            context=context or {},
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

    async def get_test_results_summary(
        self, task_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get test results summary for a task to include in approval decision.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Dict with test summary or None if no results
        """
        try:
            results = await self._substrate.search_packets_by_type(
                packet_type="test_results",
                limit=10,
            )
            
            for result in results:
                if result.get("payload", {}).get("parent_task_id") == task_id:
                    payload = result["payload"]
                    return {
                        "tests_generated": payload.get("tests_generated", 0),
                        "tests_passed": payload.get("tests_passed", 0),
                        "tests_failed": payload.get("tests_failed", 0),
                        "coverage_percent": payload.get("coverage_percent"),
                        "recommendations": payload.get("recommendations", []),
                        "success": payload.get("success", False),
                    }
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to get test results for task {task_id}: {e}")
            return None

    def format_approval_request_with_tests(
        self,
        task_id: str,
        proposal_summary: str,
        test_summary: Optional[Dict[str, Any]],
    ) -> str:
        """
        Format an approval request message including test results.
        
        Args:
            task_id: Task identifier
            proposal_summary: Summary of the proposal
            test_summary: Test results summary from get_test_results_summary
            
        Returns:
            Formatted approval request string
        """
        parts = [
            f"**APPROVAL REQUEST: {task_id[:8]}...**\n",
            f"**Proposal:** {proposal_summary}\n",
        ]
        
        if test_summary:
            parts.append("\n**Test Results:**")
            parts.append(f"- Tests Generated: {test_summary['tests_generated']}")
            parts.append(f"- Tests Passed: {test_summary['tests_passed']}")
            parts.append(f"- Tests Failed: {test_summary['tests_failed']}")
            
            if test_summary.get("coverage_percent") is not None:
                parts.append(f"- Coverage: {test_summary['coverage_percent']}%")
            
            if test_summary.get("recommendations"):
                parts.append("\n**Recommendations:**")
                for rec in test_summary["recommendations"][:3]:
                    parts.append(f"- {rec}")
            
            if test_summary["tests_failed"] > 0:
                parts.append("\n⚠️ **WARNING: Tests failed. Review before approving.**")
            elif test_summary["tests_generated"] == 0:
                parts.append("\n⚠️ **WARNING: No tests generated for this proposal.**")
        else:
            parts.append("\n*No test results available for this proposal.*")
        
        parts.append("\n\nReply with 'approve' or 'reject [reason]'")
        
        return "\n".join(parts)

    async def _write_governance_pattern(
        self,
        task_id: str,
        decision: DecisionType,
        reason: str,
        tool_name: str,
        task_type: str,
        context: Dict[str, Any],
    ) -> None:
        """
        Write a governance pattern to memory for closed-loop learning.

        Args:
            task_id: Task identifier
            decision: Approved or rejected
            reason: Reason for decision
            tool_name: Tool involved
            task_type: Type of task
            context: Additional context
        """
        # Extract conditions from reason text
        conditions = extract_conditions_from_reason(reason)

        # Create pattern
        pattern = GovernancePattern(
            task_id=task_id,
            tool_name=tool_name,
            task_type=task_type,
            decision=decision,
            reason=reason,
            context=context,
            conditions=conditions,
        )

        # Write to governance_patterns segment
        try:
            await self._substrate.write_packet(
                packet_in=PacketEnvelopeIn(
                    packet_type="governance_pattern",
                    payload=pattern.to_packet_payload(),
                    metadata={
                        "segment": "governance_patterns",
                        "searchable": True,
                    },
                )
            )
            logger.info(
                f"Governance pattern created for task {task_id}",
                decision=decision.value,
                conditions=conditions,
            )
        except Exception as e:
            logger.warning(f"Failed to write governance pattern: {e}")
