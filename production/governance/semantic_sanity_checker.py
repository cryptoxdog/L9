"""
Semantic Sanity Checker - Directive validation
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class SemanticSanityChecker:
    """
    Semantic Sanity Checker
    
    Validates that directives make semantic sense:
    - No contradictions
    - Valid parameters
    - Logical consistency
    """
    
    def __init__(self):
        """Initialize sanity checker."""
        logger.info("Semantic sanity checker initialized")
    
    def check(self, directive: dict) -> dict:
        """
        Check directive for semantic sanity.
        
        Args:
            directive: Directive to check
            
        Returns:
            Check result with issues if any
        """
        logger.debug(f"Checking directive sanity: {directive.get('command')}")
        
        issues = []
        
        # 1. Check structure
        structure_issues = self._check_structure(directive)
        if structure_issues:
            issues.extend(structure_issues)
        
        # 2. Check contradictions
        contradiction_issues = self._check_contradictions(directive)
        if contradiction_issues:
            issues.extend(contradiction_issues)
        
        # 3. Check parameters
        parameter_issues = self._check_parameters(directive)
        if parameter_issues:
            issues.extend(parameter_issues)
        
        # 4. Check logical consistency
        logic_issues = self._check_logic(directive)
        if logic_issues:
            issues.extend(logic_issues)
        
        return {
            "sane": len(issues) == 0,
            "issues": issues
        }
    
    def _check_structure(self, directive: dict) -> List[str]:
        """Check directive structure."""
        issues = []
        
        # Must be dict
        if not isinstance(directive, dict):
            issues.append("Directive must be a dict")
            return issues  # Can't check further if not a dict
        
        # Must have 'command' field
        if "command" not in directive:
            issues.append("Missing required 'command' field")
        elif not directive["command"]:
            issues.append("'command' field is empty")
        elif not isinstance(directive["command"], str):
            issues.append("'command' must be a string")
        
        # Check for empty directive
        if len(directive) == 0:
            issues.append("Directive is empty")
        
        # Check for None values in critical fields
        if directive.get("command") is None:
            issues.append("'command' cannot be None")
        
        return issues
    
    def _check_contradictions(self, directive: dict) -> List[str]:
        """Check for contradictions."""
        issues = []
        
        # Check for contradictory flags
        if directive.get("enable") and directive.get("disable"):
            if directive["enable"] == directive["disable"]:
                issues.append("Cannot enable and disable the same thing simultaneously")
        
        if directive.get("create") and directive.get("delete"):
            issues.append("Cannot create and delete simultaneously")
        
        if directive.get("start") and directive.get("stop"):
            issues.append("Cannot start and stop simultaneously")
        
        # Check for contradictory commands
        command = directive.get("command", "").lower()
        if "enable" in command and "disable" in command:
            issues.append("Command contains contradictory enable/disable")
        
        if "create" in command and "delete" in command:
            issues.append("Command contains contradictory create/delete")
        
        # Check for self-referential contradictions
        if directive.get("validate") == False and "validate" in command:
            issues.append("Cannot request validation while disabling validation")
        
        return issues
    
    def _check_parameters(self, directive: dict) -> List[str]:
        """Check parameter validity."""
        issues = []
        
        # Check for None/null in required fields
        command = directive.get("command")
        if command and not isinstance(command, str):
            issues.append("Command must be a string")
        
        return issues
    
    def _check_logic(self, directive: dict) -> List[str]:
        """Check logical consistency."""
        issues = []
        
        # Check for logical impossibilities
        if directive.get("count", 0) < 0:
            issues.append("Count cannot be negative")
        
        if directive.get("probability", 0.5) > 1.0 or directive.get("probability", 0.5) < 0.0:
            issues.append("Probability must be between 0 and 1")
        
        return issues

