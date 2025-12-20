"""
07_execution_kernel → Execution Engine / State Machine

In your execution engine module (or where you plan to put it).
"""

_KERNELS = None


def _get_kernels():
    """Lazy load kernel stack."""
    global _KERNELS
    if _KERNELS is None:
        from runtime.kernel_loader import load_kernel_stack
        _KERNELS = load_kernel_stack()
    return _KERNELS


def get_execution_state_machine() -> dict:
    return _get_kernels().get_kernel("execution") or {}


def get_allowed_transitions(state: str) -> list:
    sm = get_execution_state_machine()
    transitions = sm.get("transitions", {})
    return transitions.get(state, [])
