"""
L9 Core Agents - Kernel-Aware Agent Registry
=============================================

Agent registry that loads kernels on startup.
This ensures L wakes up with proper identity.

Version: 1.0.0
"""

from __future__ import annotations

import structlog
import os
from typing import Any, Dict, Optional

from core.agents.schemas import AgentConfig

logger = structlog.get_logger(__name__)

# Check if kernels should be used
USE_KERNELS = os.getenv("L9_USE_KERNELS", "true").lower() in ("true", "1", "yes")


class KernelAwareAgentRegistry:
    """
    Agent registry that integrates kernel loading.
    
    On initialization:
    1. Loads L-CTO agent with kernels (if USE_KERNELS=true)
    2. Crashes if kernel loading fails (as per Loading Instructions)
    3. Provides kernel-aware agent configs
    """
    
    def __init__(self):
        """Initialize the registry with kernel-loaded agents."""
        self._agents: Dict[str, AgentConfig] = {}
        self._l_cto_agent = None
        self._kernel_system_prompt: Optional[str] = None
        
        if USE_KERNELS:
            self._initialize_with_kernels()
        else:
            logger.warning("kernel_registry: L9_USE_KERNELS=false, using fallback prompts")
            self._initialize_fallback()
    
    def _initialize_with_kernels(self) -> None:
        """Initialize L-CTO agent with kernels."""
        try:
            from runtime.kernel_loader import load_kernels, require_kernel_activation
            from agents.l_cto import LCTOAgent
            
            logger.info("kernel_registry: initializing L-CTO with kernels...")
            
            # Create L-CTO agent
            agent = LCTOAgent(agent_id="l9-standard-v1")
            
            # Load kernels (this is THE choke point)
            agent = load_kernels(agent)
            
            # Hard crash if activation failed
            require_kernel_activation(agent)
            
            # Store reference
            self._l_cto_agent = agent
            
            # Get the kernel-built system prompt
            self._kernel_system_prompt = agent.get_system_prompt()
            
            # Register as agent config
            self._agents["l9-standard-v1"] = AgentConfig(
                agent_id="l9-standard-v1",
                personality_id="l-cto",
                system_prompt=self._kernel_system_prompt,
                model=os.getenv("L9_LLM_MODEL", "gpt-4o"),
                temperature=0.3,
                max_tokens=4000,
            )
            
            # Also register as "l-cto" alias
            self._agents["l-cto"] = self._agents["l9-standard-v1"]
            
            logger.info(
                "kernel_registry: L-CTO initialized with %d kernels, state=%s",
                len(agent.kernels),
                agent.kernel_state,
            )
            logger.info("kernel_registry: L identity confirmed: %s", agent.describe_self()[:100])
            
        except Exception as e:
            logger.critical("kernel_registry: FATAL - kernel loading failed: %s", e)
            raise RuntimeError(
                f"FATAL: Kernel activation failed. No tools. No Mac-Agent. No execution. Error: {e}"
            ) from e
    
    def _initialize_fallback(self) -> None:
        """Initialize with fallback prompt (no kernels)."""
        fallback_prompt = """You are L9, an AI assistant.

WARNING: Kernels not loaded. Operating in degraded mode.

Be helpful, concise, and direct."""
        
        self._agents["l9-standard-v1"] = AgentConfig(
            agent_id="l9-standard-v1",
            personality_id="fallback",
            system_prompt=fallback_prompt,
            model=os.getenv("L9_LLM_MODEL", "gpt-4o"),
            temperature=0.3,
            max_tokens=4000,
        )
    
    def get_agent_config(self, agent_id: str) -> Optional[AgentConfig]:
        """
        Get agent configuration by ID.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            AgentConfig or None if not found
        """
        config = self._agents.get(agent_id)
        if config:
            return config
        
        # If agent not found, return default with kernel prompt
        if self._kernel_system_prompt:
            return AgentConfig(
                agent_id=agent_id,
                personality_id="l-cto",
                system_prompt=self._kernel_system_prompt,
            )
        
        return None
    
    def agent_exists(self, agent_id: str) -> bool:
        """Check if agent exists."""
        # For now, accept any agent ID (all use L-CTO kernel prompt)
        return True
    
    def get_l_cto_agent(self):
        """Get the L-CTO agent instance (if loaded with kernels)."""
        return self._l_cto_agent
    
    def get_kernel_state(self) -> str:
        """Get kernel state."""
        if self._l_cto_agent:
            return self._l_cto_agent.kernel_state
        return "NOT_LOADED"


def create_kernel_aware_registry() -> KernelAwareAgentRegistry:
    """
    Create a kernel-aware agent registry.
    
    This is the proper way to create an agent registry.
    
    Returns:
        KernelAwareAgentRegistry with kernels loaded
        
    Raises:
        RuntimeError: If kernel loading fails (when USE_KERNELS=true)
    """
    return KernelAwareAgentRegistry()


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "KernelAwareAgentRegistry",
    "create_kernel_aware_registry",
]

