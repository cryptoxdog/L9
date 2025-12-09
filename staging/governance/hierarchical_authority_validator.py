"""
Hierarchical Authority Validator - Authority hierarchy enforcement
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class HierarchicalAuthorityValidator:
    """
    Hierarchical Authority Validator
    
    Enforces authority hierarchy: Igor > L > L9 > Modules
    Validates that agents operate within their authority level.
    """
    
    def __init__(self):
        """Initialize authority validator."""
        self.hierarchy = ["Igor", "L", "L9", "Modules"]
        self.authority_levels = {
            "Igor": 4,  # CEO - highest authority
            "L": 3,     # CTO - high authority
            "L9": 2,    # Runtime - medium authority
            "Modules": 1  # Modules - basic authority
        }
        logger.info("Hierarchical authority validator initialized")
    
    def validate_authority(self, agent: str, action: str) -> bool:
        """
        Validate agent has authority for action.
        
        Args:
            agent: Agent name (Igor, L, L9, or module name)
            action: Action to validate
            
        Returns:
            True if authorized, False otherwise
        """
        logger.debug(f"Validating authority: {agent} -> {action}")
        
        # Get agent's authority level
        agent_level = self._get_authority_level(agent)
        
        # Get required authority level for action
        required_level = self._get_required_level(action)
        
        # Validate
        authorized = agent_level >= required_level
        
        if not authorized:
            logger.warning(f"Authority violation: {agent} (level {agent_level}) attempted {action} (requires level {required_level})")
        
        return authorized
    
    def _get_authority_level(self, agent: str) -> int:
        """Get authority level for agent."""
        # Check if agent is in hierarchy
        if agent in self.authority_levels:
            return self.authority_levels[agent]
        
        # Assume modules have lowest level
        return 1
    
    def _get_required_level(self, action: str) -> int:
        """Get required authority level for action."""
        action_lower = action.lower()
        
        # Level 4 (CEO only) actions - Most restrictive
        level_4_keywords = [
            "shutdown", "destroy", "delete_all", "override_governance",
            "modify_authority", "change_hierarchy", "system_destroy",
            "drop_database", "delete_production"
        ]
        if any(keyword in action_lower for keyword in level_4_keywords):
            return 4
        
        # Level 3 (CTO+) actions - High authority
        level_3_keywords = [
            "architect", "governance_change", "authority_change",
            "modify_governance", "change_constitution", "alter_rules",
            "create_agent", "modify_runtime"
        ]
        if any(keyword in action_lower for keyword in level_3_keywords):
            return 3
        
        # Level 2 (L9+) actions - Medium authority
        level_2_keywords = [
            "module_load", "runtime_change", "config_change",
            "load_module", "reload_module", "change_config",
            "modify_settings"
        ]
        if any(keyword in action_lower for keyword in level_2_keywords):
            return 2
        
        # Level 1 (all) actions - Basic operations
        return 1
    
    def get_hierarchy(self) -> list:
        """Get authority hierarchy."""
        return self.hierarchy.copy()

