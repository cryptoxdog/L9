import os
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel

import api.db as db

# Local dev mode flag
import os
LOCAL_DEV = os.getenv("LOCAL_DEV", "false").lower() == "true"
from api.auth import verify_api_key
from api.memory.router import router as memory_router
from openai import OpenAI

# Integration settings
from config.settings import settings

# Initialize DB ONCE at boot
if not LOCAL_DEV:
    db.init_db()

# Create unified app (wraps the base server)
app = FastAPI(title="L9 Phase 2 Secure AI OS")

# OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not configured")
client = OpenAI(api_key=OPENAI_API_KEY)

class ChatRequest(BaseModel):
    message: str
    system_prompt: str | None = None

class ChatResponse(BaseModel):
    reply: str

@app.get("/")
def root():
    return {"status": "L9 Phase 2 AI OS", "version": "0.3.0"}

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "L9 Phase 2 Memory System",
        "version": "0.3.0",
        "database": "connected",
        "memory_system": "operational",
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    authorization: str = Header(None),
    _: bool = Depends(verify_api_key),
):
    """
    Basic LLM chat endpoint using OpenAI.
    Ingests both request and response to memory for audit trail.
    """
    from memory.ingestion import ingest_packet
    from memory.substrate_models import PacketEnvelopeIn
    
    try:
        messages = []
        if payload.system_prompt:
            messages.append({"role": "system", "content": payload.system_prompt})
        else:
            messages.append({
                "role": "system",
                "content": (
                    "You are L, an infrastructure-focused assistant connected to an L9 "
                    "backend and memory system. Be concise, precise, and avoid destructive "
                    "actions. When appropriate, suggest using tools like the CTO agent."
                ),
            })
        messages.append({"role": "user", "content": payload.message})

        completion = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
        )
        reply = completion.choices[0].message.content
        
        # Ingest chat interaction to memory (audit trail)
        try:
            packet_in = PacketEnvelopeIn(
                packet_type="chat_interaction",
                payload={
                    "user_message": payload.message,
                    "system_prompt": payload.system_prompt,
                    "assistant_reply": reply,
                    "model": "gpt-4.1-mini",
                },
                metadata={"agent": "chat_api", "source": "server_memory"},
            )
            await ingest_packet(packet_in)
        except Exception as mem_err:
            # Log but don't fail the request if memory ingestion fails
            import logging
            logging.getLogger(__name__).warning(f"Failed to ingest chat to memory: {mem_err}")
        
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat backend error: {e}")

# Mount memory router with prefix
app.include_router(memory_router, prefix="/memory")

# === Integration Routers (gated by toggle flags) ===

# Slack Events API
if settings.slack_app_enabled:
    try:
        from api.webhook_slack import router as slack_router
        app.include_router(slack_router)
    except Exception as e:
        print(f"WARNING: Failed to load Slack router: {e}")

# Mac Agent API
if settings.mac_agent_enabled:
    try:
        from api.webhook_mac_agent import router as mac_agent_router
        app.include_router(mac_agent_router)
    except Exception as e:
        print(f"WARNING: Failed to load Mac Agent router: {e}")

# Twilio webhook router (disabled until ready)
if settings.twilio_enabled:
    try:
        from api.webhook_twilio import router as twilio_router
        app.include_router(twilio_router)
    except Exception as e:
        print(f"WARNING: Failed to load Twilio router: {e}")

# WABA (WhatsApp Business Account - native Meta) (disabled until ready)
if settings.waba_enabled:
    try:
        from api.webhook_waba import router as waba_router
        app.include_router(waba_router)
    except Exception as e:
        print(f"WARNING: Failed to load WABA router: {e}")

# Email integration
if settings.email_enabled:
    try:
        from api.webhook_email import router as email_router
        app.include_router(email_router)
    except Exception as e:
        print(f"WARNING: Failed to load Email router: {e}")
    
    # Email Agent API
    try:
        from email_agent.router import router as email_agent_router
        app.include_router(email_agent_router)
    except Exception as e:
        print(f"WARNING: Failed to load Email Agent router: {e}")

# === Debug: Print integration toggles at startup ===
print("L9 Integration Toggles:", {
    "Slack": settings.slack_app_enabled,
    "Mac Agent": settings.mac_agent_enabled,
    "Email": settings.email_enabled,
    "Inbox Parser": settings.inbox_parser_enabled,
    "Twilio": settings.twilio_enabled,
    "WABA": settings.waba_enabled,
})

# === DEBUG: Print all mounted routes at startup ===
for route in app.routes:
    print("ROUTE:", route.path)
