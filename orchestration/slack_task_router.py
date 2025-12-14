"""
L9 Slack Task Router
====================

Converts Slack messages + file artifacts into Mac Agent task structures.

Version: 1.0.0
"""

import json
import logging
import os
from typing import Dict, Any, List

from openai import OpenAI

logger = logging.getLogger(__name__)

MODEL = os.getenv("L9_LLM_MODEL", "gpt-4o-mini")

def get_client() -> OpenAI:
    """Get OpenAI client."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    return OpenAI(api_key=api_key)


def route_slack_message(text: str, artifacts: List[Dict[str, Any]], user: str) -> Dict[str, Any]:
    """
    Convert Slack message + file artifacts into Mac Agent task structure.
    
    Args:
        text: User message text
        artifacts: List of file artifact dictionaries from slack_files.py
        user: Slack user ID
    
    Returns:
        Task dictionary with type, steps, artifacts, and metadata
    """
    client = get_client()
    
    system_prompt = """You are L9 Planner v2. When the instruction is about email (reading, drafting, replying, forwarding, summarizing, searching), output a JSON email_task. Otherwise, output a mac_task.

You must ALWAYS output valid JSON. Include steps for browser or email depending on intent.

Output format MUST be:
{
  "type": "mac_task" | "email_task",
  "steps": [
     // For mac_task:
     {"action": "goto", "url": "..."},
     {"action": "click", "selector": "text=..."},
     {"action": "fill", "selector": "#field", "text": "..."},
     {"action": "upload", "selector": "#file", "file_path": "<local_path>"},
     {"action": "screenshot"},
     
     // For email_task:
     {"action": "list_messages", "query": "...", "max_results": 10},
     {"action": "get_message", "message_id": "..."},
     {"action": "draft_email", "to": "...", "subject": "...", "body": "..."},
     {"action": "send_email", "draft_id": "..."}  // or {"action": "send_email", "to": "...", "subject": "...", "body": "..."}
     {"action": "reply_to_email", "message_id": "...", "body": "..."},
     {"action": "forward_email", "message_id": "...", "to": "...", "body": "..."}
  ],
  "artifacts": [...],
  "metadata": {
     "user": "<slack_user>",
     "instructions": "<raw user text>"
  }
}

No other keys allowed.

Available mac_task actions:
- goto: Navigate to URL
- click: Click element (use selector like "text=Submit" or "#button-id")
- fill: Fill input field (selector, text)
- upload: Upload file (selector, file_path - use path from artifacts)
- screenshot: Take screenshot
- wait: Wait for element (selector, optional timeout_ms)

Available email_task actions:
- list_messages: Search emails (query: Gmail search string, max_results: number)
- get_message: Get full message (message_id: Gmail message ID)
- draft_email: Create draft (to, subject, body)
- send_email: Send email (draft_id OR to/subject/body)
- reply_to_email: Reply to message (message_id, body)
- forward_email: Forward message (message_id, to, body)

When files are attached, use their "path" field as file_path in upload actions.
If artifacts contain OCR/PDF/transcription data, use that information in your steps.

CRITICAL: Choose "email_task" type when user wants to:
- Read, search, draft, send, reply, forward emails
- Check inbox, summarize emails
- Any Gmail/email operation

Choose "mac_task" type for browser automation, web scraping, or non-email tasks."""

    # Build user message with artifact context
    user_message = f"User request: {text}\n\n"
    
    if artifacts:
        user_message += "Attached files:\n"
        for artifact in artifacts:
            user_message += f"- {artifact.get('name', 'unknown')} ({artifact.get('type', 'unknown')}) at {artifact.get('path', 'unknown')}\n"
            
            # Include OCR data if available
            if artifact.get("ocr"):
                ocr_data = artifact["ocr"]
                user_message += f"  OCR text: {ocr_data.get('text', '')[:200]}...\n"
                user_message += f"  OCR confidence: {ocr_data.get('confidence', 0):.1f}%\n"
            
            # Include PDF data if available
            if artifact.get("pdf"):
                pdf_data = artifact["pdf"]
                user_message += f"  PDF summary: {pdf_data.get('summary', '')}\n"
                if pdf_data.get("fields"):
                    user_message += f"  PDF fields: {pdf_data.get('fields')}\n"
            
            # Include transcription if available
            if artifact.get("transcription"):
                trans_data = artifact["transcription"]
                user_message += f"  Transcription: {trans_data.get('text', '')[:200]}...\n"
        
        user_message += "\n"
    
    user_message += "Generate the task JSON structure based on the user's intent."
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
            response_format={"type": "json_object"} if MODEL.startswith("gpt-4") else None,
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse JSON response
        # Try to extract JSON if wrapped in markdown
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            content = content[start:end].strip()
        elif "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            content = content[start:end].strip()
        
        task_dict = json.loads(content)
        
        # Validate structure - allow both mac_task and email_task
        task_type = task_dict.get("type")
        if task_type not in ["mac_task", "email_task"]:
            logger.warning(f"Task type is not 'mac_task' or 'email_task', got: {task_type}")
            # Infer type from text
            text_lower = text.lower()
            if any(keyword in text_lower for keyword in ["email", "send", "draft", "inbox", "message"]):
                task_dict["type"] = "email_task"
            else:
                task_dict["type"] = "mac_task"
        
        # Ensure required fields
        if "steps" not in task_dict:
            task_dict["steps"] = []
        if "artifacts" not in task_dict:
            task_dict["artifacts"] = artifacts
        if "metadata" not in task_dict:
            task_dict["metadata"] = {}
        
        task_dict["metadata"]["user"] = user
        task_dict["metadata"]["instructions"] = text
        
        # Replace artifact paths in steps if needed
        if artifacts and task_dict.get("steps"):
            artifact_paths = {a.get("name"): a.get("path") for a in artifacts}
            for step in task_dict["steps"]:
                if step.get("action") == "upload":
                    # Check both "file" and "file_path" keys
                    file_ref = step.get("file") or step.get("file_path")
                    if file_ref:
                        # If file is a name, replace with path
                        if file_ref in artifact_paths:
                            step["file_path"] = artifact_paths[file_ref]
                            if "file" in step:
                                del step["file"]  # Remove "file" key, use "file_path"
                        elif not os.path.exists(file_ref):
                            # If path doesn't exist, try to find by name
                            for artifact in artifacts:
                                if artifact.get("name") == file_ref or artifact.get("path") == file_ref:
                                    step["file_path"] = artifact.get("path")
                                    if "file" in step:
                                        del step["file"]
                                    break
        
        logger.info(f"Routed Slack message to task with {len(task_dict.get('steps', []))} steps")
        return task_dict
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM JSON response: {e}")
        logger.error(f"Response was: {content[:500]}")
        # Return minimal valid structure
        return {
            "type": "mac_task",
            "steps": [],
            "artifacts": artifacts,
            "metadata": {
                "user": user,
                "instructions": text,
            }
        }
    except Exception as e:
        logger.error(f"Error routing Slack message: {e}", exc_info=True)
        # Return minimal valid structure
        return {
            "type": "mac_task",
            "steps": [],
            "artifacts": artifacts,
            "metadata": {
                "user": user,
                "instructions": text,
            }
        }

