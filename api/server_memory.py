import os
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel

import api.db as db
from api.auth import verify_api_key
from api.memory.router import router as memory_router
from openai import OpenAI

# Initialize DB ONCE at boot
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
def chat(
    payload: ChatRequest,
    authorization: str = Header(None),
    _: bool = Depends(verify_api_key),
):
    """
    Basic LLM chat endpoint using OpenAI.
    """
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
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat backend error: {e}")

# Mount memory router with prefix
app.include_router(memory_router, prefix="/memory")

# Twilio webhook router will be mounted from webhook_twilio.py
try:
    from api.webhook_twilio import router as twilio_router
    app.include_router(twilio_router)
except Exception as e:
    # Do not crash core service if Twilio routing fails; log instead.
    print(f"WARNING: Failed to load Twilio router: {e}")

# === WABA (WhatsApp Business Account - native Meta) ===
try:
    from api.webhook_waba import router as waba_router
    app.include_router(waba_router)
except Exception as e:
    # Do not crash core service if WABA routing fails; log instead.
    print(f"WARNING: Failed to load WABA router: {e}")

# === DEBUG: Print all mounted routes at startup ===
for route in app.routes:
    print("ROUTE:", route.path)
