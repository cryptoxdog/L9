"""
L9 Core Governance - Package
============================

Governance policy engine for deny-by-default enforcement.

Exports:
- GovernanceEngineService: Main policy evaluation service
- Policy, EvaluationRequest, EvaluationResult: Core schemas
- PolicyLoader: Loads policies from YAML manifests

Version: 1.0.0
"""

from core.governance.schemas import (
    Policy,
    PolicyEffect,
    Condition,
    ConditionOperator,
    EvaluationRequest,
    EvaluationResult,
)
from core.governance.loader import PolicyLoader, load_policies_from_directory
from core.governance.engine import GovernanceEngineService
from core.governance.validation import (
    validate_authority,
    validate_safety,
    detect_drift,
    audit_log,
    get_audit_trail,
)
from core.governance.mistake_prevention import (
    MistakePrevention,
    MistakeRule,
    Violation,
    Severity,
    create_mistake_prevention,
)
from core.governance.quick_fixes import (
    QuickFixEngine,
    QuickFix,
    FixResult,
    create_quick_fix_engine,
)
from core.governance.session_startup import (
    SessionStartup,
    StartupFile,
    PreflightResult,
    StartupResult,
    create_session_startup,
)
from core.governance.credentials_policy import (
    CredentialsPolicy,
    SecretPattern,
    SecretViolation,
    SecretType,
    create_credentials_policy,
)

__all__ = [
    # Service
    "GovernanceEngineService",
    # Schemas
    "Policy",
    "PolicyEffect",
    "Condition",
    "ConditionOperator",
    "EvaluationRequest",
    "EvaluationResult",
    # Loader
    "PolicyLoader",
    "load_policies_from_directory",
    # Validation
    "validate_authority",
    "validate_safety",
    "detect_drift",
    "audit_log",
    "get_audit_trail",
    # Mistake Prevention (from repeated-mistakes.md)
    "MistakePrevention",
    "MistakeRule",
    "Violation",
    "Severity",
    "create_mistake_prevention",
    # Quick Fixes (from quick-fixes.md)
    "QuickFixEngine",
    "QuickFix",
    "FixResult",
    "create_quick_fix_engine",
    # Session Startup (from session-startup-protocol.md)
    "SessionStartup",
    "StartupFile",
    "PreflightResult",
    "StartupResult",
    "create_session_startup",
    # Credentials Policy (from credentials-policy.md)
    "CredentialsPolicy",
    "SecretPattern",
    "SecretViolation",
    "SecretType",
    "create_credentials_policy",
]
