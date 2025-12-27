---
# === GMP ACTION TIER HEADER ===
tier: "ACTION"
canonical_reference: "docs/_GMP Execute + Audit/GMP-Action-Prompt-Canonical-v1.0.md"
phase_delegation: "Phases 1-6 execute per canonical protocol"
report_required: true
report_path_template: "/Users/ib-mac/Projects/L9/reports/GMP_Report_{gmp_id}.md"
---

> **⚠️ EXECUTION PROTOCOL:** This is an Action Tier prompt. It defines SCOPE, OBJECTIVE, and TODO items only. Phase execution (1–6), validation gates, and report generation follow the Canonical GMP v1.0 protocol.

## **GMP-11: GMP-L.igor-command-interface-with-intent-extraction**

You are C. You are not designing a new CLI. You are giving Igor a structured command syntax and natural language fallback to instruct L imperatively, with intent extraction ensuring clarity before high-risk execution.

### OBJECTIVE (LOCKED)

Ensure that:
1. Igor can use structured commands like `@L propose gmp: <description>` or natural language `@L analyze the current VPS state`.
2. L extracts intent (from structured syntax or NLP), confirms understanding, and executes.
3. High-risk commands are queued for explicit confirmation before execution.
4. All Igor commands are logged to audit trail.

### SCOPE (LOCKED)

You MAY modify:
- New file: `core/commands/parser.py` – parse structured commands and NLP.
- New file: `core/commands/intent_extractor.py` – extract intent and confirm with Igor.
- New file: `core/commands/executor.py` – execute commands as L tasks.
- `api/server.py` – add POST `/commands/execute` endpoint (and expose via Slack, WS, etc.).
- `core/agents/executor.py` – mark command-initiated tasks with metadata for logging.

You MAY NOT:
- Modify L's reasoning or tool behavior.
- Change approval gates (commands still go through them if high-risk).

### TODO LIST (BY ID)

**T1 – Structured command parser**
- File: `core/commands/parser.py` (new)
- Implement:
  - `parse_command(text) -> Command | NLPPrompt`
  - Recognizes patterns:
    - `@L propose gmp: <description>` → `Command(type="propose_gmp", target_description=...)`
    - `@L analyze <entity>` → `Command(type="analyze", entity_id=...)`
    - `@L approve <task_id>` → `Command(type="approve", task_id=...)`
    - `@L rollback <change_id>` → `Command(type="rollback", change_id=...)`
  - Falls back to NLPPrompt for conversational input.

**T2 – Intent extraction for NLP**
- File: `core/commands/intent_extractor.py` (new)
- Implement:
  - `extract_intent(nlp_text) -> IntentModel`
  - Uses IR engine (Intent Representation) from your architecture or LLM prompting.
  - Returns: `intent_type` (propose, analyze, approve, query, etc.), `confidence`, `entities`, `ambiguities`.

**T3 – Confirmation flow**
- File: `core/commands/intent_extractor.py`, function:
  - `async def confirm_intent(intent, user_context) -> ConfirmationResult`
  - For high-risk commands, generate a summary and ask Igor: "I understood you want to {action}. Should I proceed?"
  - Log confirmation to audit trail.

**T4 – Command executor**
- File: `core/commands/executor.py` (new)
- Implement:
  - `async def execute_command(command: Command, user_id: str) -> Result`
  - Routes command to appropriate handler:
    - `command.type == "propose_gmp"` → create AgentTask with `gmprun` tool, set `consensus_required=True`.
    - `command.type == "analyze"` → create task to query world model or memory.
    - `command.type == "approve"` → call `ApprovalManager.approvetask()` (Igor-only).
    - `command.type == "rollback"` → enqueue rollback task.
  - Returns `Result(success, message, task_id)`.

**T5 – API endpoint for commands**
- File: `api/server.py`, add POST `/commands/execute`
- Request: `{user_id (Igor auth required), command_text, context (optional)}`
- Calls `parse_command()` or `extract_intent()`.
- Confirms with Igor if high-risk.
- Calls `execute_command()`.
- Returns `Result` with task ID.

**T6 – Command logging**
- File: `core/compliance/auditlog.py`, extend
- Add `action="command"` audit entries for Igor commands.
- Include: command_text, parsed intent, user, timestamp, execution_result.

**T7 – Multi-channel command input**
- File: `api/slack_adapter.py` (extend), `api/server.py` (extend), etc.
- Detect `@L` mentions in Slack messages or structured prefixes in HTTP requests.
- Route to `parse_command()` and `/commands/execute` endpoint.

**T8 – Integration test**
- File: `tests/integration/test_igor_commands.py` (new)
- Test structured commands: `@L propose gmp`, `@L approve`, `@L analyze`.
- Test NLP: natural language command + intent extraction.
- Verify high-risk commands require confirmation.
- Verify all commands are logged to audit trail.

### PHASE 0 – RESEARCH & TODO LOCK

1. Confirm IR engine (Intent Representation) or LLM capability exists for intent extraction.
2. Verify Igor authentication/authorization is in place for `/commands/execute`.

### PHASES 1–6

Validation:
- **Positive:** Issue structured command, L executes correctly; NLP command is disambiguated and confirmed.
- **Negative:** Ambiguous commands return clarification request; high-risk commands require confirmation.
- **Regression:** Existing agent interactions unchanged; commands are additional channel.

***
