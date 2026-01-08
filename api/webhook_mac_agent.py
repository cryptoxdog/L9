"""
Mac Agent API endpoints for polling and reporting task results.
"""

import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from services.mac_tasks import get_next_task, complete_task, list_tasks

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/mac", tags=["mac-agent"])


class TaskResultRequest(BaseModel):
    """Request model for task result submission."""

    result: str
    status: str = "done"
    screenshot_path: Optional[str] = None
    logs: Optional[List[str]] = None


@router.get("/tasks/next")
def get_next_mac_task():
    """
    Get the next queued Mac task.
    Returns null if no task is available.
    """
    task = get_next_task()
    if task is None:
        return {"task": None}

    task_dict = {
        "id": task.id,
        "source": task.source,
        "channel": task.channel,
        "user": task.user,
    }

    # Include command (legacy) or steps (V2)
    if task.command:
        task_dict["command"] = task.command
    if task.steps:
        task_dict["steps"] = task.steps

    # Include file attachments if present
    if task.attachments:
        task_dict["attachments"] = task.attachments

    return {"task": task_dict}


@router.post("/tasks/{task_id}/result")
async def submit_task_result(task_id: int, payload: TaskResultRequest):
    """
    Submit the result of a Mac task execution.
    If source is "slack" and channel is set, posts result back to Slack.
    Ingests result to memory for audit trail.
    """
    task = complete_task(
        task_id,
        payload.result,
        payload.status,
        screenshot_path=payload.screenshot_path,
        logs=payload.logs,
    )

    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    # Ingest task result to memory (audit trail)
    try:
        from memory.ingestion import ingest_packet
        from memory.substrate_models import PacketEnvelopeIn

        packet_in = PacketEnvelopeIn(
            packet_type="mac_task_result",
            payload={
                "task_id": task_id,
                "status": payload.status,
                "result": payload.result[:2000]
                if payload.result
                else None,  # Truncate large results
                "has_screenshot": bool(payload.screenshot_path),
                "log_count": len(payload.logs) if payload.logs else 0,
                "source": task.source,
                "user": task.user,
            },
            metadata={"agent": "mac_agent", "source": "webhook_mac_agent"},
        )
        await ingest_packet(packet_in)
    except Exception as e:
        logger.warning(f"Failed to ingest task result to memory: {e}")

    # If source is slack and channel is set, post back to Slack
    if task.source == "slack" and task.channel:
        try:
            from services.slack_client import slack_post

            status_emoji = "✅" if payload.status == "done" else "❌"

            # Build message with enhanced V2 info
            message_parts = [
                f"{status_emoji} Mac task {task_id} finished with status `{payload.status}`"
            ]

            if payload.logs:
                # Include last few logs
                recent_logs = (
                    payload.logs[-5:] if len(payload.logs) > 5 else payload.logs
                )
                message_parts.append("\nRecent logs:")
                for log in recent_logs:
                    message_parts.append(f"  • {log}")

            message_parts.append(
                f"\n```\n{payload.result[:500]}{'...' if len(payload.result) > 500 else ''}\n```"
            )

            if payload.screenshot_path:
                message_parts.append(f"\n📸 Screenshot: {payload.screenshot_path}")

            message = "\n".join(message_parts)
            slack_post(task.channel, message)
            logger.info(
                f"[MAC-AGENT] Posted result for task {task_id} to Slack channel {task.channel}"
            )
        except Exception as e:
            logger.error(f"[MAC-AGENT] Failed to post result to Slack: {e}")
            # Don't fail the request if Slack posting fails

    return {"ok": True}


@router.get("/tasks")
def list_mac_tasks():
    """
    List all Mac tasks (for debugging).
    """
    tasks = list_tasks()
    return {"tasks": tasks}

# ============================================================================
# L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT
# ============================================================================
__dora_block__ = {
    "component_id": "API-OPER-007",
    "component_name": "Webhook Mac Agent",
    "module_version": "1.0.0",
    "created_at": "2026-01-08T03:15:13Z",
    "created_by": "L9_DORA_Injector",
    "layer": "operations",
    "domain": "api_gateway",
    "type": "utility",
    "status": "active",
    "governance_level": "medium",
    "compliance_required": True,
    "audit_trail": True,
    "purpose": "Implements TaskResultRequest for webhook mac agent functionality",
    "dependencies": [],
}

# ============================================================================
# END L9 DORA BLOCK
# ============================================================================
