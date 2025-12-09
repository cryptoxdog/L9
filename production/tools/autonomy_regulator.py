"""
Autonomy Regulator - Prevent autonomy escalation
"""
import logging

logger = logging.getLogger(__name__)


class AutonomyRegulator:
    """
    Autonomy Regulator
    
    Prevents agents from escalating their autonomy level.
    Enforces maximum autonomy level (L = 2).
    """
    
    def __init__(self):
        """Initialize autonomy regulator."""
        self.max_autonomy_level = 2  # L's level
        self.agent_levels = {
            "Igor": 4,
            "L": 2,
            "L9": 1,
            "Modules": 0
        }
        logger.info(f"Autonomy regulator initialized (max level: {self.max_autonomy_level})")
    
    def check_autonomy(self, agent: str, action: str) -> bool:
        """
        Check if action is within agent's autonomy bounds.
        
        Args:
            agent: Agent name
            action: Action to validate
            
        Returns:
            True if within bounds, False otherwise
        """
        agent_level = self.agent_levels.get(agent, 0)
        required_level = self._get_required_autonomy(action)
        
        within_bounds = agent_level >= required_level
        
        if not within_bounds:
            logger.warning(f"Autonomy violation: {agent} (level {agent_level}) attempted action requiring level {required_level}")
        
        return within_bounds
    
    def _get_required_autonomy(self, action: str) -> int:
        """Get required autonomy level for action."""
        action_lower = action.lower()
        
        # Level 2+ actions
        if any(keyword in action_lower for keyword in ["architect", "design", "govern"]):
            return 2
        
        # Level 1+ actions
        if any(keyword in action_lower for keyword in ["execute", "run", "process"]):
            return 1
        
        # Level 0+ actions (all)
        return 0
    
    def prevent_escalation(self, agent: str, new_level: int) -> bool:
        """
        Prevent autonomy escalation.
        
        Args:
            agent: Agent name
            new_level: Requested new autonomy level
            
        Returns:
            True if allowed, False if escalation detected
        """
        current_level = self.agent_levels.get(agent, 0)
        
        if new_level > current_level:
            logger.error(f"Autonomy escalation blocked: {agent} attempted {current_level} → {new_level}")
            return False
        
        return True

