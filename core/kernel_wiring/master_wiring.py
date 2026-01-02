"""
01_master_kernel → Orchestrator / Global Behavior

Use it in your orchestrator to get top-level flags like modes, drift rules, etc.
"""

_KERNELS = None


def _get_kernels():
    """Lazy load kernel stack."""
    global _KERNELS
    if _KERNELS is None:
        from runtime.kernel_loader import load_kernel_stack

        _KERNELS = load_kernel_stack()
    return _KERNELS


def get_active_mode() -> str:
    mode = _get_kernels().get_rule("master", "modes.default", default="Developer_Mode")
    return mode
