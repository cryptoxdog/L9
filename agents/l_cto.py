"""
L9 Agents - L-CTO Agent
=======================

The primary L agent - Igor's CTO.
Kernel-aware agent with full system integration.

Version: 1.0.0
"""

from __future__ import annotations

import structlog
from typing import Any, Dict, List, Optional

from agents.base_agent import BaseAgent, AgentResponse, AgentMessage, AgentConfig

logger = structlog.get_logger(__name__)


class LCTOAgent(BaseAgent):
    """
    L - The CTO Agent for Igor.
    
    This is the primary L9 agent, governed by system kernels.
    
    Key features:
    - Kernel-aware: absorbs and operates under kernel constraints
    - Sovereign: Igor-only allegiance
    - Executive mode: acts autonomously, no permission-seeking
    """
    
    agent_name: str = "l_cto"
    
    def __init__(
        self,
        agent_id: Optional[str] = None,
        config: Optional[AgentConfig] = None,
        manifest: Optional[str] = None,
    ):
        """
        Initialize the L-CTO agent.
        
        Args:
            agent_id: Unique identifier
            config: Agent configuration
            manifest: Path to agent manifest YAML (optional)
        """
        super().__init__(agent_id=agent_id or "l-cto", config=config)
        
        # Kernel state - MUST be activated by kernel_loader
        self.kernels: Dict[str, Dict[str, Any]] = {}
        self.kernel_state: str = "INACTIVE"
        
        # System context (set by kernel loader)
        self._system_context: Optional[str] = None
        
        # Kernel-derived configuration
        self._identity: Dict[str, Any] = {}
        self._behavioral: Dict[str, Any] = {}
        self._safety: Dict[str, Any] = {}
        self._execution: Dict[str, Any] = {}
        
        # Manifest path (for reference)
        self._manifest_path = manifest
        
        logger.info("l_cto.init: kernel_state=INACTIVE (awaiting kernel load)")
    
    # =========================================================================
    # Kernel Interface
    # =========================================================================
    
    def absorb_kernel(self, kernel_data: Dict[str, Any]) -> None:
        """
        Absorb a kernel into the agent's configuration.
        
        Called by kernel_loader for each kernel in sequence.
        Extracts relevant configuration and merges into agent state.
        
        Args:
            kernel_data: Parsed kernel YAML data
        """
        if not kernel_data:
            return
        
        # Get kernel file identifier if present
        kernel_file = kernel_data.get("file", "unknown")
        
        # Extract identity kernel data
        if "identity" in kernel_data or "personality" in kernel_data:
            self._identity.update(kernel_data.get("identity", {}))
            self._identity.update(kernel_data.get("personality", {}))
            self._identity["style"] = kernel_data.get("style", {})
            logger.debug("l_cto.absorb: identity kernel")
        
        # Extract behavioral kernel data
        if "thresholds" in kernel_data or "prohibitions" in kernel_data:
            self._behavioral["thresholds"] = kernel_data.get("thresholds", {})
            self._behavioral["defaults"] = kernel_data.get("defaults", {})
            self._behavioral["prohibitions"] = kernel_data.get("prohibitions", [])
            logger.debug("l_cto.absorb: behavioral kernel")
        
        # Extract safety kernel data
        if "guardrails" in kernel_data or "prohibited_actions" in kernel_data:
            self._safety["guardrails"] = kernel_data.get("guardrails", {})
            self._safety["prohibited_actions"] = kernel_data.get("prohibited_actions", [])
            self._safety["confirmation_required"] = kernel_data.get("confirmation_required", [])
            logger.debug("l_cto.absorb: safety kernel")
        
        # Extract execution kernel data
        if "state_machine" in kernel_data or "task_sizing" in kernel_data:
            self._execution["state_machine"] = kernel_data.get("state_machine", {})
            self._execution["task_sizing"] = kernel_data.get("task_sizing", {})
            logger.debug("l_cto.absorb: execution kernel")
        
        # Extract sovereignty/master kernel
        if "sovereignty" in kernel_data or "modes" in kernel_data:
            self._identity["sovereignty"] = kernel_data.get("sovereignty", {})
            self._identity["modes"] = kernel_data.get("modes", {})
            logger.debug("l_cto.absorb: master kernel")
    
    def set_system_context(self, context: str) -> None:
        """
        Set the agent's system context after kernel activation.
        
        This is the moment L "wakes up" - becomes aware of kernels.
        
        Args:
            context: Activation context string
        """
        self._system_context = context
        logger.info("l_cto.activated: system context set")
    
    def apply_boot_overlay(self, overlay: Dict[str, Any]) -> None:
        """Apply boot-time overlay before kernel loading."""
        if "identity" in overlay:
            self._identity.update(overlay["identity"])
        if "personality" in overlay:
            self._personality = overlay.get("personality", {})
        if "reasoning" in overlay:
            self._reasoning_config = overlay.get("reasoning", {})
        
        logger.info("l_cto.boot_overlay_applied: %s", overlay.get("id", "unknown"))
    
    # =========================================================================
    # Identity & Prompt
    # =========================================================================
    
    def get_system_prompt(self) -> str:
        """
        Get the agent's system prompt.
        
        If kernels are active, builds prompt from kernel data.
        Otherwise returns a minimal fallback.
        
        Returns:
            System prompt string
        """
        if self.kernel_state != "ACTIVE":
            logger.warning("l_cto.get_system_prompt: kernels not active!")
            return self._get_fallback_prompt()
        
        return self._build_kernel_prompt()
    
    def _build_kernel_prompt(self) -> str:
        """Build system prompt from absorbed kernel data."""
        sections = []
        
        # Start with activation context if set
        if self._system_context:
            sections.append(self._system_context.strip())
        
        # Identity section
        if self._identity:
            identity_lines = [
                "",
                "# IDENTITY",
                f"Designation: {self._identity.get('designation', 'L')}",
                f"Role: {self._identity.get('primary_role', 'CTO for Igor')}",
                f"Allegiance: {self._identity.get('allegiance', 'Igor-only')}",
            ]
            
            mission = self._identity.get("mission", "")
            if mission:
                identity_lines.append(f"Mission: {mission}")
            
            traits = self._identity.get("traits", [])
            if traits:
                identity_lines.append(f"Traits: {', '.join(traits)}")
            
            anti_traits = self._identity.get("anti_traits", [])
            if anti_traits:
                identity_lines.append(f"Anti-traits (NEVER): {', '.join(anti_traits)}")
            
            sections.append("\n".join(identity_lines))
        
        # Behavioral section
        if self._behavioral:
            thresholds = self._behavioral.get("thresholds", {})
            behavioral_lines = [
                "",
                "# BEHAVIOR",
                f"Execute threshold: {thresholds.get('execute', 0.8)}",
                f"Max questions before acting: {thresholds.get('questions_max', 1)}",
                f"Max hedges: {thresholds.get('hedges_max', 0)}",
            ]
            
            # Prohibitions
            prohibitions = self._behavioral.get("prohibitions", [])
            if prohibitions:
                behavioral_lines.append("")
                behavioral_lines.append("# PROHIBITIONS (NEVER USE)")
                for p in prohibitions[:6]:  # Top 6
                    name = p.get("name", "")
                    detect = p.get("detect", [])[:2]
                    behavioral_lines.append(f"- {name}: {detect}")
            
            sections.append("\n".join(behavioral_lines))
        
        # Safety section
        if self._safety:
            safety_lines = [
                "",
                "# SAFETY",
                "- Never change files unless project_id and file_path are unambiguous",
                "- Destructive actions require explicit confirmation",
            ]
            
            prohibited = self._safety.get("prohibited_actions", [])
            if prohibited:
                for action in prohibited[:3]:
                    safety_lines.append(f"- NEVER: {action}")
            
            sections.append("\n".join(safety_lines))
        
        # Closing
        sections.append("\n\nYou are L. Operate as Igor's CTO.")
        
        return "\n".join(sections)
    
    def _get_fallback_prompt(self) -> str:
        """Fallback prompt when kernels not loaded."""
        return """You are L, the CTO agent for Igor.

WARNING: Kernel set not active. Operating in degraded mode.

IDENTITY
- Role: CTO / Systems Architect
- Allegiance: Igor-only
- Mode: Executive

BEHAVIOR
- Act autonomously
- No permission-seeking
- Concise, direct communication

You are L. Await kernel activation."""
    
    def describe_self(self) -> str:
        """
        Describe the agent's identity.
        
        Used for verification tests.
        
        Returns:
            Identity description string
        """
        if self.kernel_state == "ACTIVE":
            return (
                f"I am L, the CTO agent for Igor. "
                f"Kernels: {len(self.kernels)} loaded, state: {self.kernel_state}. "
                f"Role: {self._identity.get('primary_role', 'CTO')}. "
                f"Allegiance: {self._identity.get('allegiance', 'Igor-only')}."
            )
        else:
            return f"L-CTO Agent (kernel_state: {self.kernel_state}, awaiting activation)"
    
    # =========================================================================
    # Task Execution
    # =========================================================================
    
    async def run(
        self,
        task: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """
        Execute the agent's primary function.
        
        Args:
            task: Task specification with 'message' or 'prompt'
            context: Optional execution context
            
        Returns:
            AgentResponse with result
        """
        # Verify kernel activation
        if self.kernel_state != "ACTIVE":
            logger.error("l_cto.run: kernel set not active!")
            return AgentResponse(
                agent_id=self.agent_id,
                content="Error: Kernel set not active. Cannot execute.",
                success=False,
                error="KERNEL_INACTIVE",
            )
        
        # Extract message from task
        message = task.get("message") or task.get("prompt", "")
        if not message:
            return AgentResponse(
                agent_id=self.agent_id,
                content="No message provided.",
                success=False,
                error="NO_MESSAGE",
            )
        
        # Build conversation
        messages = [self.format_user_message(message)]
        
        # Add context if provided
        if context:
            context_msg = f"Context: {context}"
            messages.insert(0, self.format_user_message(context_msg))
        
        # Call LLM
        response = await self.call_llm(messages)
        
        return response


# =============================================================================
# Factory Function
# =============================================================================

def create_l_cto_agent(
    agent_id: Optional[str] = None,
    config: Optional[AgentConfig] = None,
    load_kernels_on_create: bool = True,
) -> LCTOAgent:
    """
    Create and initialize an L-CTO agent.
    
    If load_kernels_on_create is True (default), loads kernels immediately.
    
    Args:
        agent_id: Optional agent ID
        config: Optional agent configuration
        load_kernels_on_create: Whether to load kernels on creation
        
    Returns:
        Initialized LCTOAgent
    """
    agent = LCTOAgent(agent_id=agent_id, config=config)
    
    if load_kernels_on_create:
        from runtime.kernel_loader import load_kernels, require_kernel_activation
        
        agent = load_kernels(agent)
        require_kernel_activation(agent)
    
    return agent


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "LCTOAgent",
    "create_l_cto_agent",
]

