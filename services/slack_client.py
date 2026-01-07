import os
import structlog

logger = structlog.get_logger(__name__)

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_ENABLED = os.getenv("SLACK_APP_ENABLED", "false").lower() == "true"

_client = None


def get_client():
    """Lazily construct a slack_sdk.WebClient if enabled and configured."""
    global _client
    if not SLACK_APP_ENABLED or not SLACK_BOT_TOKEN:
        return None
    if _client is None:
        try:
            from slack_sdk import WebClient

            _client = WebClient(token=SLACK_BOT_TOKEN)
        except ImportError:
            logger.error("[SLACK] slack_sdk not installed")
            return None
        except Exception as e:
            logger.error(f"[SLACK] Failed to create client: {e}")
            return None
    return _client


def slack_post(channel: str, text: str):
    """
    Post a message to a Slack channel.
    No-ops if Slack is disabled or not configured.
    Logs errors, doesn't crash the app.
    """
    client = get_client()
    if not client:
        logger.debug("[SLACK] No client; skipping send")
        return
    try:
        response = client.chat_postMessage(channel=channel, text=text)
        logger.info(f"[SLACK] Posted message to {channel}")
        return response
    except Exception as e:
        logger.error(f"[SLACK] Error posting message: {e}")
        # Don't raise - fail silently


def post_result(user: str, task: dict, result: dict):
    """
    Post execution summary + screenshots back to Slack.

    Args:
        user: Slack user ID (for DM) or channel ID
        task: Task dictionary with metadata
        result: Execution result dictionary with status, logs, screenshots
    """
    client = get_client()
    if not client:
        logger.debug("[SLACK] No client; skipping result post")
        return

    try:
        task_id = task.get(
            "task_id", task.get("metadata", {}).get("task_id", "unknown")
        )
        status = result.get("status", "unknown")
        logs = result.get("logs", [])
        screenshots = result.get("screenshots", [])
        # Backward compatibility: check screenshot_path if screenshots not available
        if not screenshots and result.get("screenshot_path"):
            screenshots = [result.get("screenshot_path")]

        steps = task.get("steps", [])
        steps_count = len(steps)

        # Count successes and failures from structured logs
        successes = sum(
            1
            for log in logs
            if isinstance(log, dict) and log.get("status") == "success"
        )
        failures = sum(
            1 for log in logs if isinstance(log, dict) and log.get("status") == "error"
        )

        # Build formatted message
        message_parts = []

        # Add warning emoji for errors
        if status == "error":
            message_parts.append("⚠️ Automation failed")

        message_parts.extend(
            [
                f"Task <{task_id}> completed.",
                f"Status: {status}",
                "",
                "Summary:",
                f"• Steps: {steps_count}",
                f"• Successes: {successes}",
                f"• Failures: {failures}",
            ]
        )

        # Add first 3 log details
        if logs:
            message_parts.append("")
            message_parts.append("Details:")
            log_details = []
            for log in logs[:3]:
                if isinstance(log, dict):
                    action = log.get("action", "unknown")
                    log_status = log.get("status", "unknown")
                    details = log.get("details", "")
                    log_details.append(
                        f"• {action}: {log_status}"
                        + (f" - {details[:50]}" if details else "")
                    )
                else:
                    log_details.append(f"• {str(log)[:100]}")
            message_parts.extend(log_details)

        # Add task-specific previews
        task_type = task.get("type", "mac_task")

        # Email task: enhanced formatting
        if task_type == "email_task":
            message_parts.append("")
            message_parts.append("📧 *Email Result:*")

            # Extract operation from steps
            steps = task.get("steps", [])
            operation = None
            for step in steps:
                action = step.get("action")
                if action in [
                    "list_messages",
                    "get_message",
                    "draft_email",
                    "send_email",
                    "reply_to_email",
                ]:
                    operation = action
                    break

            if operation:
                operation_display = {
                    "list_messages": "Search",
                    "get_message": "Read",
                    "draft_email": "Draft",
                    "send_email": "Send",
                    "reply_to_email": "Reply",
                }.get(operation, operation)
                message_parts.append(f"Operation: {operation_display}")

            # Show email details from result data
            result_data = result.get("data", {})

            # Messages found
            if "messages" in result_data:
                messages = result_data["messages"]
                message_parts.append(f"Found {len(messages)} message(s):")
                for msg in messages[:3]:  # Show first 3
                    message_parts.append(
                        f"  • {msg.get('subject', 'No subject')} from {msg.get('from', 'Unknown')}"
                    )
                if len(messages) > 3:
                    message_parts.append(f"  ... and {len(messages) - 3} more")

            # Message retrieved
            if "message" in result_data:
                msg = result_data["message"]
                message_parts.append("")
                message_parts.append(f"*Subject:* {msg.get('subject', 'No subject')}")
                message_parts.append(f"*From:* {msg.get('from', 'Unknown')}")
                message_parts.append(f"*To:* {msg.get('to', 'Unknown')}")
                if msg.get("attachments"):
                    message_parts.append(
                        f"*Attachments:* {len(msg['attachments'])} file(s)"
                    )
                body_preview = msg.get("body_plain", msg.get("body_html", ""))[:200]
                if body_preview:
                    message_parts.append(f"*Preview:* {body_preview}...")

            # Draft created
            if "draft_id" in result_data:
                message_parts.append("")
                message_parts.append(f"✅ Draft created: {result_data['draft_id']}")
                # Show draft details from steps
                for step in steps:
                    if step.get("action") == "draft_email":
                        message_parts.append(f"To: {step.get('to', 'N/A')}")
                        message_parts.append(f"Subject: {step.get('subject', 'N/A')}")
                        body_preview = step.get("body", "")[:150]
                        if body_preview:
                            message_parts.append(f"Body: {body_preview}...")
                        break

            # Email sent
            if "message_id" in result_data:
                message_parts.append("")
                message_parts.append("✅ Email sent successfully")
                message_parts.append(f"Message ID: {result_data['message_id']}")
                if result_data.get("thread_id"):
                    message_parts.append(f"Thread ID: {result_data['thread_id']}")

            # Reply sent
            if operation == "reply_to_email" and result.get("status") == "success":
                message_parts.append("")
                message_parts.append("✅ Reply sent successfully")

            # Fallback: show step details if no data
            if not result_data and steps:
                for step in steps:
                    if step.get("action") == "draft_email":
                        message_parts.append("")
                        message_parts.append("Email Draft:")
                        message_parts.append(f"To: {step.get('to', 'N/A')}")
                        message_parts.append(f"Subject: {step.get('subject', 'N/A')}")
                        message_parts.append(f"Body: {step.get('body', '')[:100]}...")
                        break

        # OCR/PDF preview from artifacts
        artifacts = task.get("artifacts", [])
        for artifact in artifacts[:2]:  # Show first 2 artifacts
            artifact_name = artifact.get("name", "unknown")

            if artifact.get("ocr"):
                ocr_data = artifact["ocr"]
                ocr_text = ocr_data.get("text", "")
                if ocr_text:
                    preview = ocr_text[:100].replace("\n", " ")
                    message_parts.append("")
                    message_parts.append(f"OCR ({artifact_name}): {preview}...")

            if artifact.get("pdf"):
                pdf_data = artifact["pdf"]
                summary = pdf_data.get("summary", "")
                if summary:
                    message_parts.append("")
                    message_parts.append(f"PDF ({artifact_name}): {summary}")
                elif pdf_data.get("fields"):
                    fields_preview = ", ".join(list(pdf_data["fields"].keys())[:3])
                    message_parts.append("")
                    message_parts.append(
                        f"PDF Fields ({artifact_name}): {fields_preview}..."
                    )

            if artifact.get("transcription"):
                trans_data = artifact["transcription"]
                trans_text = trans_data.get("text", "")
                if trans_text:
                    preview = trans_text[:100].replace("\n", " ")
                    message_parts.append("")
                    message_parts.append(
                        f"Transcription ({artifact_name}): {preview}..."
                    )

        message = "\n".join(message_parts)

        # Upload screenshots
        uploaded_files = []
        for screenshot_path in screenshots:
            if screenshot_path and os.path.exists(screenshot_path):
                try:
                    with open(screenshot_path, "rb") as f:
                        file_response = client.files_upload_v2(
                            channel=user,
                            file=f,
                            title=f"Task {task_id} screenshot",
                            filename=os.path.basename(screenshot_path),
                        )
                    uploaded_files.append(file_response)
                    logger.info(
                        f"[SLACK] Uploaded screenshot: {os.path.basename(screenshot_path)}"
                    )
                except Exception as e:
                    logger.error(
                        f"[SLACK] Failed to upload screenshot {screenshot_path}: {e}"
                    )

        # If no screenshots were uploaded but we have screenshot_path (backward compat)
        if (
            not uploaded_files
            and result.get("screenshot_path")
            and os.path.exists(result.get("screenshot_path"))
        ):
            try:
                with open(result["screenshot_path"], "rb") as f:
                    file_response = client.files_upload_v2(
                        channel=user,
                        file=f,
                        title=f"Task {task_id} screenshot",
                        filename=os.path.basename(result["screenshot_path"]),
                    )
                    uploaded_files.append(file_response)
            except Exception as e:
                logger.error(f"[SLACK] Failed to upload screenshot: {e}")

        # Post message
        response = client.chat_postMessage(channel=user, text=message)
        logger.info(
            f"[SLACK] Posted result for task {task_id} to {user} ({len(uploaded_files)} screenshots)"
        )
        return response

    except Exception as e:
        logger.error(f"[SLACK] Error posting result: {e}", exc_info=True)
        # Don't raise - fail silently
