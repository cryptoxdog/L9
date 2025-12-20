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
]
