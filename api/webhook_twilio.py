import os
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import PlainTextResponse
import httpx

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_SMS_NUMBER = os.getenv("TWILIO_SMS_NUMBER")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
EXECUTOR_API_KEY = os.getenv("L9_EXECUTOR_API_KEY")

if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_SMS_NUMBER, EXECUTOR_API_KEY]):
    raise RuntimeError("Twilio or executor environment variables not fully configured")

router = APIRouter()

CHAT_URL = "http://127.0.0.1:8000/chat"

@router.post("/twilio/webhook", response_class=PlainTextResponse)
async def twilio_webhook(request: Request):
    """
    Minimal Twilio SMS/WhatsApp webhook:
    - Reads incoming message body and from number
    - Forwards text to /chat
    - Returns plain text reply in TwiML-compatible form
    """
    form = await request.form()
    from_number = form.get("From")
    body = form.get("Body")

    if not body:
        raise HTTPException(status_code=400, detail="Missing Body")

    prompt = f"Message from {from_number}: {body}"

    async with httpx.AsyncClient(timeout=20) as client:
        try:
            resp = await client.post(
                CHAT_URL,
                json={"message": prompt},
                headers={"Authorization": f"Bearer {EXECUTOR_API_KEY}"},
            )
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Chat call failed: {e}")

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    data = resp.json()
    reply = data.get("reply", "I could not generate a response.")

    # Twilio expects plain text for simple replies (it will wrap into SMS)
    return PlainTextResponse(reply)
