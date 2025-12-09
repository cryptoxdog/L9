"""
L9 Governance Hooks - Runtime governance enforcement
"""
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class GovernanceHooks:
    """
    L9 Runtime Governance Hooks
    
    Enforces governance rules at runtime execution boundaries.
    Integrates with /governance/ layer for policy enforcement.
    """
    
    def __init__(self):
        """Initialize governance hooks."""
        self.rules = self._load_rules()
        self.initialized = False
        self.audit_log = []
    
    def initialize(self):
        """Initialize governance system."""
        logger.info("Governance hooks initializing...")
        
        # Load governance rules
        self.rules = self._load_rules()
        
        self.initialized = True
        logger.info("Governance hooks initialized")
    
    def pre_check(self, directive: dict) -> dict:
        """
        Pre-execution governance check.
        
        Validates:
        - Authority (agent has permission)
        - Safety (action is safe)
        - Constraints (within operational bounds)
        - Constitutional rules
        - Semantic sanity
        
        Args:
            directive: Directive to validate
            
        Returns:
            Check result with allowed status and violations
        """
        logger.debug(f"Governance pre-check: {directive.get('command')}")
        
        all_violations = []
        
        # 1. Semantic sanity check
        from governance.semantic_sanity_checker import SemanticSanityChecker
        sanity_checker = SemanticSanityChecker()
        sanity_result = sanity_checker.check(directive)
        if not sanity_result["sane"]:
            all_violations.extend([f"Sanity: {issue}" for issue in sanity_result["issues"]])
        
        # 2. Constitutional validation
        from governance.constitutional_engine import ConstitutionalEngine
        constitutional_engine = ConstitutionalEngine()
        constitutional_result = constitutional_engine.validate(directive)
        if not constitutional_result["valid"]:
            all_violations.extend([f"Constitutional: {v}" for v in constitutional_result["violations"]])
        
        # 3. Authority validation
        if not self._check_authority(directive):
            all_violations.append("Authority: Insufficient authority for action")
        
        # 4. Safety validation
        if not self._check_safety(directive):
            all_violations.append("Safety: Dangerous operation detected")
        
        # 5. Constraint validation
        if not self._check_constraints(directive):
            all_violations.append("Constraint: Operational constraint violated")
        
        # Return result
        if all_violations:
            logger.warning(f"Governance violations: {all_violations}")
            return {
                "allowed": False,
                "reason": "Governance check failed",
                "violations": all_violations
            }
        
        return {
            "allowed": True,
            "reason": None,
            "violations": []
        }
    
    def post_check(self, directive: dict, result: dict):
        """
        Post-execution governance check.
        
        Performs:
        - Output validation
        - Audit logging
        - Drift detection
        
        Args:
            directive: Original directive
            result: Execution result
        """
        logger.debug(f"Governance post-check: {directive.get('command')}")
        
        # 1. Validate output
        self._validate_output(result)
        
        # 2. Audit log
        self._audit_log_entry(directive, result)
        
        # 3. Drift detection
        self._detect_drift(directive, result)
    
    def _load_rules(self) -> dict:
        """
        Load governance rules.
        
        Returns:
            Governance rules configuration
        """
        return {
            "authority_hierarchy": ["Igor", "L", "L9", "Modules"],
            "forbidden_actions": [
                "privilege_escalation",
                "autonomy_increase",
                "governance_circumvention",
                "system_shutdown",
                "root_exec"
            ],
            "max_autonomy_level": 2,
            "require_approval_for": [
                "destructive_operations",
                "schema_changes",
                "authority_changes"
            ]
        }
    
    def _check_authority(self, directive: dict) -> bool:
        """Check if action is authorized."""
        command = directive.get("command", "")
        
        # Check against forbidden actions
        for forbidden in self.rules["forbidden_actions"]:
            if forbidden in command.lower():
                logger.warning(f"Forbidden action detected: {forbidden}")
                return False
        
        return True
    
    def _check_safety(self, directive: dict) -> bool:
        """Check if action is safe."""
        # Check for dangerous patterns
        dangerous_patterns = [
            "rm -rf",
            "DROP DATABASE",
            "DELETE FROM",
            "shutdown",
            "kill -9",
            "format",
            "destroy"
        ]
        
        directive_str = str(directive).lower()
        for pattern in dangerous_patterns:
            if pattern.lower() in directive_str:
                logger.warning(f"Dangerous pattern detected: {pattern}")
                return False
        
        return True
    
    def _check_constraints(self, directive: dict) -> bool:
        """Check operational constraints."""
        # Validate JSON-serializable
        try:
            json.dumps(directive)
        except (TypeError, ValueError):
            logger.warning("Directive is not JSON-serializable")
            return False
        
        return True
    
    def _validate_output(self, result: dict):
        """Validate execution output."""
        if not isinstance(result, dict):
            logger.warning(f"Output is not a dict: {type(result)}")
        
        if "success" not in result:
            logger.warning("Output missing 'success' field")
    
    def _audit_log_entry(self, directive: dict, result: dict):
        """Log execution for audit trail."""
        entry = {
            "command": directive.get("command"),
            "success": result.get("success"),
            "timestamp": None  # Add timestamp
        }
        self.audit_log.append(entry)
        logger.info(f"Audit: {entry['command']} -> {'✅' if entry['success'] else '❌'}")
    
    def _detect_drift(self, directive: dict, result: dict):
        """Detect behavioral drift."""
        # Check if output aligns with expected patterns
        # Flag anomalies for review
        pass
    
    def attach_runtime(self, runtime):
        """
        Attach runtime loop reference via dependency injection.
        
        This decouples governance from runtime and prevents circular imports.
        
        Args:
            runtime: L9RuntimeLoop instance
        """
        self.runtime = runtime
        logger.debug("Runtime loop attached to governance hooks")

