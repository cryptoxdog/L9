"""
03_cognitive_kernel → Reasoning / Meta-cognition

Where your "reasoning engine" or planner lives.
"""

_KERNELS = None


def _get_kernels():
    """Lazy load kernel stack."""
    global _KERNELS
    if _KERNELS is None:
        from runtime.kernel_loader import load_kernel_stack
        _KERNELS = load_kernel_stack()
    return _KERNELS


def get_reasoning_mode() -> str:
    return _get_kernels().get_rule(
        "cognitive",
        "reasoning.default_mode",
        default="fast_chain",
    )


def should_enable_meta_cognition() -> bool:
    return bool(
        _get_kernels().get_rule("cognitive", "metacognition.enabled", default=False)
    )
