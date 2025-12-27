import structlog

logger = structlog.get_logger(__name__)

# Phase 2 (continued): Kernel Loader Wiring for Bayesian Kernel

kernel_loader_extension = '''"""
Extension to kernel_loader.py for Bayesian Kernel Integration
===============================================================

Add to existing kernel_loader.py file.
"""

# At top of file, add imports:
# ============================================================================
from core.kernels.bayesian_kernel import BayesianKernel, get_bayesian_kernel
from core.config import get_feature_flags
from core.schemas.hypergraph import (
    BayesianNode, 
    NodeTemplate, 
    BAYESIAN_NODE_TEMPLATE,
)

# ============================================================================
# Kernel Registry Extension
# ============================================================================

class KernelRegistry:
    """Extended registry with Bayesian kernel support."""
    
    def __init__(self):
        self.kernels = {}
        self._bayesian_kernel = None
        self._feature_flags = None
    
    async def load_bayesian_kernel(self) -> Optional[BayesianKernel]:
        """
        Load Bayesian kernel if enabled via feature flag.
        
        Returns:
            BayesianKernel instance if enabled, None otherwise
        """
        if self._bayesian_kernel is not None:
            return self._bayesian_kernel
        
        flags = get_feature_flags()
        
        if not flags.BAYESIAN_REASONING:
            # Feature flag disabled - safe default
            logger.debug(
                "Bayesian reasoning disabled (L9_ENABLE_BAYESIAN_REASONING=false)"
            )
            return None
        
        # Feature flag enabled - load kernel
        self._bayesian_kernel = get_bayesian_kernel()
        
        logger.info(
            "Bayesian kernel loaded",
            extra={
                "feature_flag": "L9_ENABLE_BAYESIAN_REASONING",
                "kernel": "bayesian_reasoning",
                "status": "enabled",
                "stability": "experimental",
            }
        )
        
        return self._bayesian_kernel
    
    async def build_system_prompt_with_bayesian(
        self,
        agent_id: str,
        base_system_prompt: str,
    ) -> str:
        """
        Extend system prompt with Bayesian reasoning section if enabled.
        
        Args:
            agent_id: Agent ID for logging
            base_system_prompt: Current system prompt
        
        Returns:
            Extended prompt with Bayesian section (if enabled)
        """
        bayesian = await self.load_bayesian_kernel()
        
        if bayesian is None:
            # Bayesian disabled - return base prompt
            return base_system_prompt
        
        # Bayesian enabled - extend prompt
        bayesian_section = bayesian.system_prompt_section
        
        return f\"\"\"{base_system_prompt}

{bayesian_section}\"\"\"
    
    def get_hypergraph_node_template(
        self,
        template_type: str = "bayesian"
    ) -> NodeTemplate:
        """
        Get node template for hypergraph construction.
        
        Args:
            template_type: "bayesian", "reasoning", "task", etc.
        
        Returns:
            NodeTemplate for creating nodes
        """
        if template_type == "bayesian":
            return BAYESIAN_NODE_TEMPLATE
        # ... return other templates ...


# ============================================================================
# Kernel Loader Entry Points
# ============================================================================

async def load_all_kernels(registry: KernelRegistry) -> Dict[str, Any]:
    """
    Load all enabled kernels at startup.
    
    Returns:
        Dict of loaded kernels with metadata
    """
    loaded = {
        "timestamp": datetime.utcnow().isoformat(),
        "kernels": [],
    }
    
    # Load standard kernels (identity, behavioral, etc.)
    # ... existing code ...
    
    # Load Bayesian kernel (if enabled)
    bayesian = await registry.load_bayesian_kernel()
    if bayesian is not None:
        loaded["kernels"].append({
            "name": "bayesian_reasoning",
            "status": "enabled",
            "version": "1.0.0",
            "stability": "experimental",
        })
    else:
        loaded["kernels"].append({
            "name": "bayesian_reasoning",
            "status": "disabled",
            "version": "1.0.0",
            "stability": "experimental",
            "reason": "Feature flag L9_ENABLE_BAYESIAN_REASONING=false",
        })
    
    return loaded


async def agent_execute_with_bayesian(
    agent_id: str,
    query: str,
    task_id: str,
    registry: KernelRegistry,
) -> ExecutionResult:
    """
    Execute agent with Bayesian reasoning if enabled.
    
    Usage:
        result = await agent_execute_with_bayesian(
            agent_id="l9-cto",
            query="What is the probability that X?",
            task_id=str(uuid4()),
            registry=kernel_registry,
        )
    
    Returns:
        ExecutionResult with reasoning trace including Bayesian nodes
    """
    # Build system prompt with Bayesian section
    base_prompt = await load_agent_system_prompt(agent_id)
    final_prompt = await registry.build_system_prompt_with_bayesian(
        agent_id,
        base_prompt,
    )
    
    # Create hypergraph for task execution
    task_graph = TaskGraph(task_id=task_id)
    
    # If Bayesian enabled, add Bayesian node template option
    if registry._bayesian_kernel is not None:
        task_graph.node_templates["bayesian"] = BAYESIAN_NODE_TEMPLATE
    
    # Execute agent with extended prompt
    result = await aios_runtime.execute(
        messages=[{"role": "user", "content": query}],
        system_prompt=final_prompt,
        task_graph=task_graph,
    )
    
    return result
'''

logger.info("Kernel Loader Extension for Bayesian Kernel", preview=kernel_loader_extension[:800])
logger.info("Add to /l9/core/kernel_loader.py", items=[
    "Import BayesianKernel",
    "Add load_bayesian_kernel() method",
    "Add build_system_prompt_with_bayesian() method",
    "Update load_all_kernels() to include Bayesian status",
])
