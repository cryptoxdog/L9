import os
import requests
from fastapi import Request
from typing import Dict, Any
from .whatsapp import send_whatsapp_message
from .llm import chat_with_l9

VPS_BASE_URL = os.getenv("L9_VPS_BASE_URL", "http://localhost:8000")

def create_mac_task(task: Dict[str, Any]) -> str | None:
    """
    Send a task to the existing /agent/tasks endpoint.
    Task format example:
      { "type": "shell", "payload": {"command": "echo hi", "timeout": 30}, "priority": 5 }
    """
    try:
        resp = requests.post(
            f"{VPS_BASE_URL}/agent/tasks",
            json=task,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("task_id")
    except Exception as e:
        # If task creation fails, just log by sending a WhatsApp back
        send_whatsapp_message(f"L9 error creating task: {e}")
        return None

async def handle_incoming_whatsapp(request: Request):
    """
    Receive a WhatsApp message from Twilio, send to LLM,
    optionally create a Mac task, and reply with the LLM's message.
    """
    form = await request.form()
    body = form.get("Body", "")
    from_number = form.get("From")  # whatsapp:+1...

    if not body:
        return "OK"

    # 1) Ask LLM what to do
    result = chat_with_l9(body)
    reply = result.get("reply", "")
    action = result.get("action", "none")
    payload = result.get("payload", {}) or {}

    # 2) If there's an action, turn it into a Mac task
    if action == "shell":
        command = payload.get("command")
        timeout = payload.get("timeout", 30)
        if command:
            task = {
                "type": "shell",
                "payload": {"command": command, "timeout": timeout},
                "priority": 5,
            }
            task_id = create_mac_task(task)
            if task_id:
                reply += f"\n\n(Task queued on Mac as {task_id})"

    # 3) Send reply to the same WhatsApp number
    send_whatsapp_message(reply, to=from_number)
    return "OK"
