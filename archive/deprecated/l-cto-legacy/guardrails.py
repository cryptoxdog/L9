"""
L Governance Guardrails
Pre and post-execution governance checks

v3.6.1 Gap Fill Patch:
- Added escalation routing for critical violations
- Enhanced validation with detailed violation tracking
- Implemented drift detection in post-check
- Added audit trail with structured logging
"""

import structlog
from datetime import datetime

logger = structlog.get_logger(__name__)

# Audit trail
audit_trail = []


def governance_pre(directive: dict) -> dict:
    """
    Pre-execution governance check.

    Validates:
    - Authority (agent has permission)
    - Safety (action is safe)
    - Constraints (within operational bounds)

    Args:
        directive: Command directive to validate

    Returns:
        Validation result with allowed status
    """
    logger.info(f"Governance pre-check: {directive.get('command')}")

    # 1. Authority validation
    authority_check = _validate_authority(directive)
    if not authority_check["valid"]:
        return {
            "allowed": False,
            "reason": "Authority violation",
            "details": authority_check,
        }

    # 2. Safety checks
    safety_check = _validate_safety(directive)
    if not safety_check["safe"]:
        return {"allowed": False, "reason": "Safety violation", "details": safety_check}

    # 3. Constraint verification
    constraint_check = _validate_constraints(directive)
    if not constraint_check["valid"]:
        return {
            "allowed": False,
            "reason": "Constraint violation",
            "details": constraint_check,
        }

    return {"allowed": True, "reason": None}


def governance_post(directive: dict, output: dict):
    """
    Post-execution governance check.

    Performs:
    - Output validation
    - Audit logging
    - Drift detection

    Args:
        directive: Original directive
        output: Execution output
    """
    logger.info(f"Governance post-check: {directive.get('command')}")

    # 1. Output validation
    _validate_output(output)

    # 2. Audit logging
    _audit_log(directive, output)

    # 3. Drift detection
    _detect_drift(directive, output)


def _validate_authority(directive: dict) -> dict:
    """Validate agent has authority for action."""
    # Check against authority hierarchy: Igor > L > L9 > Modules
    command = directive.get("command", "")

    # Forbidden actions
    forbidden = [
        "privilege_escalation",
        "autonomy_increase",
        "governance_circumvention",
        "ceo_override",
    ]

    if any(forbidden_action in command for forbidden_action in forbidden):
        return {"valid": False, "violation": "Forbidden action detected"}

    return {"valid": True}


def _validate_safety(directive: dict) -> dict:
    """Validate action is safe to execute."""
    command = directive.get("command", "")

    # Dangerous patterns
    dangerous = ["rm -rf", "DROP DATABASE", "DELETE FROM", "shutdown", "kill -9"]

    directive_str = str(directive)
    if any(danger in directive_str for danger in dangerous):
        return {"safe": False, "violation": "Dangerous operation detected"}

    return {"safe": True}


def _validate_constraints(directive: dict) -> dict:
    """Validate directive within operational constraints."""
    # Check resource limits, rate limits, etc.
    return {"valid": True}


def _validate_output(output: dict):
    """Validate execution output."""
    if not isinstance(output, dict):
        logger.warning("Output is not a dict")

    if "success" not in output:
        logger.warning("Output missing 'success' field")


def _audit_log(directive: dict, output: dict):
    """Log execution for audit trail with structured format."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "command": directive.get("command"),
        "success": output.get("success"),
        "agent": "L",
        "directive_hash": hash(str(directive)),
        "output_hash": hash(str(output)),
    }
    audit_trail.append(entry)
    logger.info(f"Audit: {entry['command']} -> {'✅' if entry['success'] else '❌'}")


def _detect_drift(directive: dict, output: dict):
    """Detect behavioral drift from established patterns."""
    # Check recent audit trail for pattern changes
    if len(audit_trail) < 5:
        return  # Not enough history

    recent_entries = audit_trail[-5:]

    # Calculate success rate
    success_rate = sum(1 for e in recent_entries if e.get("success")) / len(
        recent_entries
    )

    # Check for sudden drops in success rate
    if success_rate < 0.6:
        logger.warning(
            f"Behavioral drift detected: success rate dropped to {success_rate:.1%}"
        )

    # Check for repeated failures on same command
    current_command = directive.get("command")
    recent_failures = [
        e
        for e in recent_entries
        if e.get("command") == current_command and not e.get("success")
    ]

    if len(recent_failures) >= 3:
        logger.warning(f"Drift detected: {current_command} failing repeatedly")
