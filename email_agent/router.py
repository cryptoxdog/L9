"""
L9 Email Agent Router
====================

FastAPI router for email agent endpoints.
Fully compliant with memory ingestion pipeline.

Version: 3.0.0

All handlers:
1. Generate trace_id
2. Ingest pre-action packet
3. Execute action
4. Ingest post-action outcome packet
5. Fail loudly if ingestion fails
"""

import structlog
from functools import wraps
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/email", tags=["email-agent"])


# =============================================================================
# Request Models
# =============================================================================

class QueryRequest(BaseModel):
    """Request model for email query."""
    query: str = ""
    max_results: int = 10


class GetRequest(BaseModel):
    """Request model for getting email."""
    id: str


class DraftRequest(BaseModel):
    """Request model for email draft."""
    to: str
    subject: str
    body: str
    attachments: Optional[List[str]] = None


class SendRequest(BaseModel):
    """Request model for sending email."""
    draft_id: Optional[str] = None
    to: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    attachments: Optional[List[str]] = None


class ReplyRequest(BaseModel):
    """Request model for replying to email."""
    id: str
    body: str


class ForwardRequest(BaseModel):
    """Request model for forwarding email."""
    id: str
    to: str
    body: str = ""


# =============================================================================
# Memory Ingestion Helper
# =============================================================================

async def ingest_email_event(
    trace_id: str,
    action: str,
    phase: str,  # "pre" or "post"
    payload: Dict[str, Any],
    error: Optional[str] = None,
) -> None:
    """
    Ingest email event to memory.
    
    Args:
        trace_id: Unique trace identifier for this request
        action: Action being performed (e.g., "email.query", "email.send")
        phase: "pre" for before action, "post" for after action
        payload: Event payload (sanitized, no secrets)
        error: Error message if action failed
        
    Raises:
        HTTPException: If ingestion fails (fail loud policy)
    """
    from memory.ingestion import ingest_packet
    from memory.substrate_models import PacketEnvelopeIn
    
    packet_type = f"email_{phase}"
    
    packet_in = PacketEnvelopeIn(
        packet_type=packet_type,
        payload={
            "trace_id": trace_id,
            "action": action,
            "phase": phase,
            **payload,
            **({"error": error} if error else {}),
        },
        metadata={
            "agent": "email_agent",
            "source": "email_api",
            "trace_id": trace_id,
        },
    )
    
    try:
        await ingest_packet(packet_in)
        logger.debug(f"[{trace_id}] Ingested email event: {action} ({phase})")
    except Exception as e:
        logger.error(f"[{trace_id}] FAILED to ingest email event: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Memory ingestion failed for {action} ({phase}): {str(e)}. trace_id={trace_id}"
        )


def generate_trace_id() -> str:
    """Generate a unique trace ID for request tracking."""
    return f"email-{uuid4().hex[:12]}"


# =============================================================================
# Email Handlers (Fully Wired)
# =============================================================================

@router.post("/query")
async def query_emails(request: QueryRequest):
    """
    Query emails using Gmail search.
    
    Ingests pre/post events to memory.
    
    Example queries:
    - "from:lawyer has:attachment"
    - "subject:meeting"
    - "is:unread"
    """
    trace_id = generate_trace_id()
    action = "email.query"
    
    # Pre-action ingestion
    await ingest_email_event(
        trace_id=trace_id,
        action=action,
        phase="pre",
        payload={
            "query": request.query,
            "max_results": request.max_results,
        },
    )
    
    try:
        from email_agent.gmail_client import GmailClient
        client = GmailClient()
        messages = client.list_messages(request.query, request.max_results)
        
        # Post-action ingestion (success)
        await ingest_email_event(
            trace_id=trace_id,
            action=action,
            phase="post",
            payload={
                "status": "success",
                "result_count": len(messages) if messages else 0,
            },
        )
        
        return {"messages": messages, "trace_id": trace_id}
        
    except HTTPException:
        raise
    except Exception as e:
        # Post-action ingestion (error)
        await ingest_email_event(
            trace_id=trace_id,
            action=action,
            phase="post",
            payload={"status": "error"},
            error=str(e),
        )
        logger.error(f"[{trace_id}] Email query failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"{str(e)} (trace_id={trace_id})")


@router.post("/get")
async def get_email(request: GetRequest):
    """
    Get full email message with parsed body and attachments.
    
    Ingests pre/post events to memory.
    
    Returns:
        Message dictionary with id, from, to, subject, date, body_plain, body_html, attachments
    """
    trace_id = generate_trace_id()
    action = "email.get"
    
    # Pre-action ingestion
    await ingest_email_event(
        trace_id=trace_id,
        action=action,
        phase="pre",
        payload={"message_id": request.id},
    )
    
    try:
        from email_agent.gmail_client import GmailClient
        client = GmailClient()
        message = client.get_message(request.id)
        
        if message:
            # Post-action ingestion (success)
            await ingest_email_event(
                trace_id=trace_id,
                action=action,
                phase="post",
                payload={
                    "status": "success",
                    "message_id": request.id,
                    "has_attachments": bool(message.get("attachments")),
                },
            )
            return {"message": message, "trace_id": trace_id}
        else:
            # Post-action ingestion (not found)
            await ingest_email_event(
                trace_id=trace_id,
                action=action,
                phase="post",
                payload={"status": "not_found", "message_id": request.id},
            )
            raise HTTPException(status_code=404, detail=f"Message {request.id} not found (trace_id={trace_id})")
            
    except HTTPException:
        raise
    except Exception as e:
        # Post-action ingestion (error)
        await ingest_email_event(
            trace_id=trace_id,
            action=action,
            phase="post",
            payload={"status": "error", "message_id": request.id},
            error=str(e),
        )
        logger.error(f"[{trace_id}] Email get failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"{str(e)} (trace_id={trace_id})")


@router.post("/draft")
async def draft_email(request: DraftRequest):
    """
    Create email draft with optional attachments.
    
    Ingests pre/post events to memory.
    """
    trace_id = generate_trace_id()
    action = "email.draft"
    
    # Pre-action ingestion (sanitized - no body content)
    await ingest_email_event(
        trace_id=trace_id,
        action=action,
        phase="pre",
        payload={
            "to": request.to,
            "subject": request.subject,
            "body_length": len(request.body) if request.body else 0,
            "attachment_count": len(request.attachments) if request.attachments else 0,
        },
    )
    
    try:
        from email_agent.gmail_client import GmailClient
        client = GmailClient()
        draft_id = client.draft_email(
            request.to,
            request.subject,
            request.body,
            attachments=request.attachments
        )
        
        if draft_id:
            # Post-action ingestion (success)
            await ingest_email_event(
                trace_id=trace_id,
                action=action,
                phase="post",
                payload={
                    "status": "success",
                    "draft_id": draft_id,
                },
            )
            return {"draft_id": draft_id, "status": "success", "trace_id": trace_id}
        else:
            # Post-action ingestion (failure)
            await ingest_email_event(
                trace_id=trace_id,
                action=action,
                phase="post",
                payload={"status": "error"},
                error="Draft creation returned None",
            )
            raise HTTPException(status_code=500, detail=f"Failed to create draft (trace_id={trace_id})")
            
    except HTTPException:
        raise
    except Exception as e:
        # Post-action ingestion (error)
        await ingest_email_event(
            trace_id=trace_id,
            action=action,
            phase="post",
            payload={"status": "error"},
            error=str(e),
        )
        logger.error(f"[{trace_id}] Email draft failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"{str(e)} (trace_id={trace_id})")


@router.post("/send")
async def send_email(request: SendRequest):
    """
    Send email (from draft or directly) with optional attachments.
    
    Ingests pre/post events to memory.
    """
    trace_id = generate_trace_id()
    action = "email.send"
    
    # Determine send mode
    send_mode = "draft" if request.draft_id else "direct"
    
    # Pre-action ingestion (sanitized)
    await ingest_email_event(
        trace_id=trace_id,
        action=action,
        phase="pre",
        payload={
            "send_mode": send_mode,
            "draft_id": request.draft_id,
            "to": request.to,
            "subject": request.subject,
            "body_length": len(request.body) if request.body else 0,
            "attachment_count": len(request.attachments) if request.attachments else 0,
        },
    )
    
    try:
        from email_agent.gmail_client import GmailClient
        client = GmailClient()
        
        if request.draft_id:
            # Send existing draft
            try:
                draft = client.service.users().drafts().get(
                    userId='me',
                    id=request.draft_id
                ).execute()
                
                sent_message = client.service.users().drafts().send(
                    userId='me',
                    body={'id': request.draft_id}
                ).execute()
                
                # Post-action ingestion (success)
                await ingest_email_event(
                    trace_id=trace_id,
                    action=action,
                    phase="post",
                    payload={
                        "status": "success",
                        "send_mode": "draft",
                        "message_id": sent_message.get('id'),
                        "thread_id": sent_message.get('threadId'),
                    },
                )
                
                return {
                    "status": "success",
                    "message": "Email sent",
                    "message_id": sent_message.get('id'),
                    "thread_id": sent_message.get('threadId'),
                    "trace_id": trace_id,
                }
            except Exception as e:
                await ingest_email_event(
                    trace_id=trace_id,
                    action=action,
                    phase="post",
                    payload={"status": "error", "send_mode": "draft"},
                    error=str(e),
                )
                logger.error(f"[{trace_id}] Failed to send draft: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to send draft: {str(e)} (trace_id={trace_id})")
        else:
            # Send directly
            if not all([request.to, request.subject, request.body]):
                await ingest_email_event(
                    trace_id=trace_id,
                    action=action,
                    phase="post",
                    payload={"status": "error", "send_mode": "direct"},
                    error="Missing required fields: to, subject, body",
                )
                raise HTTPException(status_code=400, detail=f"to, subject, and body required for direct send (trace_id={trace_id})")
            
            result = client.send_email(
                request.to,
                request.subject,
                request.body,
                attachments=request.attachments
            )
            
            if result:
                # Post-action ingestion (success)
                await ingest_email_event(
                    trace_id=trace_id,
                    action=action,
                    phase="post",
                    payload={
                        "status": "success",
                        "send_mode": "direct",
                        "provider_response": result,
                    },
                )
                return {
                    "status": "success",
                    "message": "Email sent",
                    "trace_id": trace_id,
                    **result
                }
            else:
                await ingest_email_event(
                    trace_id=trace_id,
                    action=action,
                    phase="post",
                    payload={"status": "error", "send_mode": "direct"},
                    error="send_email returned None",
                )
                raise HTTPException(status_code=500, detail=f"Failed to send email (trace_id={trace_id})")
                
    except HTTPException:
        raise
    except Exception as e:
        await ingest_email_event(
            trace_id=trace_id,
            action=action,
            phase="post",
            payload={"status": "error"},
            error=str(e),
        )
        logger.error(f"[{trace_id}] Email send failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"{str(e)} (trace_id={trace_id})")


@router.post("/reply")
async def reply_email(request: ReplyRequest):
    """
    Reply to an email message.
    
    Ingests pre/post events to memory.
    
    Args:
        id: Original message ID to reply to
        body: Reply body
    """
    trace_id = generate_trace_id()
    action = "email.reply"
    
    # Pre-action ingestion
    await ingest_email_event(
        trace_id=trace_id,
        action=action,
        phase="pre",
        payload={
            "original_message_id": request.id,
            "body_length": len(request.body) if request.body else 0,
        },
    )
    
    try:
        from email_agent.gmail_client import GmailClient
        client = GmailClient()
        result = client.reply_to_email(request.id, request.body)
        
        if result:
            # Post-action ingestion (success)
            await ingest_email_event(
                trace_id=trace_id,
                action=action,
                phase="post",
                payload={
                    "status": "success",
                    "original_message_id": request.id,
                    "provider_response": result,
                },
            )
            return {
                "status": "success",
                "message": "Reply sent",
                "trace_id": trace_id,
                **result
            }
        else:
            await ingest_email_event(
                trace_id=trace_id,
                action=action,
                phase="post",
                payload={"status": "error", "original_message_id": request.id},
                error="reply_to_email returned None",
            )
            raise HTTPException(status_code=500, detail=f"Failed to send reply (trace_id={trace_id})")
            
    except HTTPException:
        raise
    except Exception as e:
        await ingest_email_event(
            trace_id=trace_id,
            action=action,
            phase="post",
            payload={"status": "error", "original_message_id": request.id},
            error=str(e),
        )
        logger.error(f"[{trace_id}] Email reply failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"{str(e)} (trace_id={trace_id})")


@router.post("/forward")
async def forward_email(request: ForwardRequest):
    """
    Forward an email message.
    
    Ingests pre/post events to memory.
    
    Args:
        id: Original message ID to forward
        to: Recipient email address(es)
        body: Optional forward message body
    """
    trace_id = generate_trace_id()
    action = "email.forward"
    
    # Pre-action ingestion
    await ingest_email_event(
        trace_id=trace_id,
        action=action,
        phase="pre",
        payload={
            "original_message_id": request.id,
            "to": request.to,
            "body_length": len(request.body) if request.body else 0,
        },
    )
    
    try:
        from email_agent.gmail_client import GmailClient
        client = GmailClient()
        result = client.forward_email(request.id, request.to, request.body)
        
        if result:
            # Post-action ingestion (success)
            await ingest_email_event(
                trace_id=trace_id,
                action=action,
                phase="post",
                payload={
                    "status": "success",
                    "original_message_id": request.id,
                    "to": request.to,
                    "provider_response": result,
                },
            )
            return {
                "status": "success",
                "message": "Email forwarded",
                "trace_id": trace_id,
                **result
            }
        else:
            await ingest_email_event(
                trace_id=trace_id,
                action=action,
                phase="post",
                payload={"status": "error", "original_message_id": request.id},
                error="forward_email returned None",
            )
            raise HTTPException(status_code=500, detail=f"Failed to forward email (trace_id={trace_id})")
            
    except HTTPException:
        raise
    except Exception as e:
        await ingest_email_event(
            trace_id=trace_id,
            action=action,
            phase="post",
            payload={"status": "error", "original_message_id": request.id},
            error=str(e),
        )
        logger.error(f"[{trace_id}] Email forward failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"{str(e)} (trace_id={trace_id})")
