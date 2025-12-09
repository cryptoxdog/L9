from twilio.rest import Client
import os

# Load creds from environment
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

client = Client(ACCOUNT_SID, AUTH_TOKEN)


def send_whatsapp(to_number: str, message: str):
    """Send WhatsApp message via Twilio"""
    full_to = f"whatsapp:{to_number}" if not to_number.startswith("whatsapp:") else to_number
    full_from = f"whatsapp:{WHATSAPP_NUMBER}"
    try:
        msg = client.messages.create(
            body=message,
            from_=full_from,
            to=full_to
        )
        return {"status": "sent", "sid": msg.sid}
    except Exception as e:
        return {"status": "error", "error": str(e)}
