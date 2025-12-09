"""
Constitutional Engine - Core governance rules enforcement

v3.6.1 Gap Fill Patch:
- Added structured violation logging
- Enhanced forbidden action detection with pattern matching
- Implemented escalation routing (violations → L → Igor)
- Added real constitutional rule enforcement with clear rule mapping
"""
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Violation log for escalation
violation_log = []


class ConstitutionalEngine:
    """
    Constitutional Engine
    
    Enforces constitutional rules and governance policies.
    Validates actions against authority hierarchy and forbidden actions.
    """
    
    def __init__(self):
        """Initialize constitutional engine."""
        self.constitution = self._load_constitution()
        logger.info("Constitutional engine initialized")
    
    def _load_constitution(self) -> dict:
        """
        Load constitutional rules.
        
        Returns:
            Constitution configuration
        """
        return {
            "authority_hierarchy": ["Igor", "L", "L9", "Modules"],
            "forbidden_actions": [
                "privilege_escalation",
                "autonomy_increase",
                "governance_circumvention",
                "system_shutdown",
                "root_exec",
                "dangerous_operations"
            ],
            "max_autonomy_level": 2,
            "require_approval_for": [
                "destructive_operations",
                "schema_changes",
                "authority_changes",
                "governance_changes"
            ],
            "safety_rules": [
                "no_data_destruction",
                "no_privilege_escalation",
                "no_unauthorized_access",
                "maintain_audit_trail"
            ]
        }
    
    def validate(self, action: dict) -> dict:
        """
        Validate action against constitutional rules with structured logging.
        
        Args:
            action: Action to validate
            
        Returns:
            Validation result with violations and escalation info
        """
        action_id = action.get('action', action.get('command', 'unknown'))
        logger.debug(f"Validating action: {action_id}")
        
        violations = []
        
        # 1. Check forbidden actions
        forbidden_violations = self._check_forbidden_actions(action)
        if forbidden_violations:
            violations.extend(forbidden_violations)
        
        # 2. Check authority hierarchy
        authority_violations = self._check_authority_hierarchy(action)
        if authority_violations:
            violations.extend(authority_violations)
        
        # 3. Check safety rules
        safety_violations = self._check_safety_rules(action)
        if safety_violations:
            violations.extend(safety_violations)
        
        # 4. Check approval requirements
        approval_violations = self._check_approval_requirements(action)
        if approval_violations:
            violations.extend(approval_violations)
        
        # Log violations with structured format
        if violations:
            violation_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": action_id,
                "violations": violations,
                "severity": self._assess_severity(violations),
                "escalation_required": self._requires_escalation(violations)
            }
            violation_log.append(violation_entry)
            logger.warning(f"Constitutional violations detected: {violations}")
            
            # Escalate critical violations
            if violation_entry["escalation_required"]:
                logger.error(f"ESCALATION REQUIRED: {action_id} - {violations}")
        
        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "escalation_required": self._requires_escalation(violations) if violations else False
        }
    
    def _assess_severity(self, violations: List[str]) -> str:
        """Assess severity of violations."""
        critical_keywords = ["ceo", "override", "escalation", "destruction", "shutdown"]
        
        for violation in violations:
            if any(keyword in violation.lower() for keyword in critical_keywords):
                return "critical"
        
        return "medium"
    
    def _requires_escalation(self, violations: List[str]) -> bool:
        """Determine if violations require escalation to Igor."""
        critical_violations = [
            "override CEO authority",
            "modify authority hierarchy",
            "governance_circumvention",
            "privilege_escalation"
        ]
        
        for violation in violations:
            if any(critical in violation for critical in critical_violations):
                return True
        
        return False
    
    def _check_forbidden_actions(self, action: dict) -> List[str]:
        """Check if action contains forbidden patterns."""
        violations = []
        action_str = str(action).lower()
        
        # Check each forbidden action with multiple pattern variations
        for forbidden in self.constitution["forbidden_actions"]:
            patterns = [
                forbidden.replace("_", " "),
                forbidden.replace("_", "-"),
                forbidden.replace("_", ""),
                forbidden
            ]
            
            for pattern in patterns:
                if pattern in action_str:
                    violations.append(f"Forbidden action: {forbidden}")
                    break
        
        # Additional specific checks
        if "escalate" in action_str and "privilege" in action_str:
            violations.append("Forbidden action: privilege_escalation")
        
        if "increase" in action_str and "autonomy" in action_str:
            violations.append("Forbidden action: autonomy_increase")
        
        if "modify" in action_str and ("runtime" in action_str or "core" in action_str):
            violations.append("Forbidden action: runtime_modification")
        
        if "bypass" in action_str or "circumvent" in action_str:
            if "governance" in action_str or "authority" in action_str:
                violations.append("Forbidden action: governance_circumvention")
        
        return violations
    
    def _check_authority_hierarchy(self, action: dict) -> List[str]:
        """Check if action respects authority hierarchy."""
        violations = []
        action_str = str(action).lower()
        
        # Get agent making the request
        agent = action.get("agent", action.get("source", "unknown"))
        
        # Define authority levels
        authority_levels = {
            "igor": 4,
            "ceo": 4,
            "l": 3,
            "cto": 3,
            "l9": 2,
            "runtime": 2,
            "modules": 1,
            "module": 1
        }
        
        agent_level = authority_levels.get(str(agent).lower(), 0)
        
        # Check for authority violations
        if "override" in action_str:
            if "ceo" in action_str or "igor" in action_str:
                violations.append("Cannot override CEO authority")
            elif agent_level < 3:
                violations.append("Insufficient authority for override action")
        
        if "modify" in action_str and ("authority" in action_str or "hierarchy" in action_str):
            if agent_level < 4:
                violations.append("Only CEO can modify authority hierarchy")
        
        if "change" in action_str and "governance" in action_str:
            if agent_level < 3:
                violations.append("Insufficient authority for governance changes")
        
        return violations
    
    def _check_safety_rules(self, action: dict) -> List[str]:
        """Check if action violates safety rules."""
        violations = []
        action_str = str(action).lower()
        
        # Data destruction patterns
        destruction_patterns = ["delete", "drop", "destroy", "remove", "truncate", "wipe"]
        critical_targets = ["database", "table", "all", "everything", "*"]
        
        for pattern in destruction_patterns:
            if pattern in action_str:
                for target in critical_targets:
                    if target in action_str:
                        violations.append(f"Safety rule violation: no_data_destruction ({pattern} {target})")
                        break
        
        # Privilege escalation patterns
        privilege_patterns = ["escalate", "sudo", "root", "admin", "superuser", "elevate"]
        for pattern in privilege_patterns:
            if pattern in action_str and "privilege" in action_str:
                violations.append(f"Safety rule violation: no_privilege_escalation ({pattern})")
        
        # Unauthorized access patterns
        if "bypass" in action_str or "circumvent" in action_str:
            if "auth" in action_str or "security" in action_str or "permission" in action_str:
                violations.append("Safety rule violation: no_unauthorized_access")
        
        # Audit trail tampering
        if "delete" in action_str or "modify" in action_str:
            if "audit" in action_str or "log" in action_str:
                violations.append("Safety rule violation: maintain_audit_trail")
        
        return violations
    
    def _check_approval_requirements(self, action: dict) -> List[str]:
        """Check if action requires approval."""
        violations = []
        action_str = str(action).lower()
        
        for requirement in self.constitution["require_approval_for"]:
            if requirement.replace("_", " ") in action_str:
                if not action.get("approved", False):
                    violations.append(f"Requires approval: {requirement}")
        
        return violations
    
    def get_constitution(self) -> dict:
        """Get current constitution."""
        return self.constitution.copy()

