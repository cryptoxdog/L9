"""
Custom exceptions for symbolic computation module.
"""


class SymbolicComputationError(Exception):
    """Base exception for symbolic computation errors."""

    def __init__(self, message: str, details: dict = None):
        """
        Initialize exception.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class EvaluationError(SymbolicComputationError):
    """Exception raised when expression evaluation fails."""
    pass


class CodeGenerationError(SymbolicComputationError):
    """Exception raised when code generation fails."""
    pass


class ValidationError(SymbolicComputationError):
    """Exception raised when input validation fails."""
    pass


class CacheError(SymbolicComputationError):
    """Exception raised when cache operations fail."""
    pass

# ============================================================================
# L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT
# ============================================================================
__dora_block__ = {
    "component_id": "SER-OPER-016",
    "component_name": "Exceptions",
    "module_version": "1.0.0",
    "created_at": "2026-01-08T03:15:14Z",
    "created_by": "L9_DORA_Injector",
    "layer": "operations",
    "domain": "symbolic_computation",
    "type": "utility",
    "status": "active",
    "governance_level": "medium",
    "compliance_required": True,
    "audit_trail": True,
    "purpose": "Provides exceptions components including SymbolicComputationError, EvaluationError, CodeGenerationError",
    "dependencies": [],
}

# ============================================================================
# END L9 DORA BLOCK
# ============================================================================
