"""
08_safety_kernel → Safety Scanners / Guardrails

In your safety layer (modules/safety/ or preflight hooks).
"""

_KERNELS = None


def _get_kernels():
    """Lazy load kernel stack."""
    global _KERNELS
    if _KERNELS is None:
        from runtime.kernel_loader import load_kernel_stack
        _KERNELS = load_kernel_stack()
    return _KERNELS


def get_safety_policies() -> dict:
    return _get_kernels().get_kernel("safety") or {}


def is_destructive_action(action: str) -> bool:
    destructive = _get_kernels().get_rule("safety", "destructive.actions", default=[]) or []
    return action in destructive
