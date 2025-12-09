"""
02_identity_kernel → Output Formatting / Persona

In your main response / formatting layer (wherever you shape responses).
"""

_KERNELS = None


def _get_kernels():
    """Lazy load kernel stack."""
    global _KERNELS
    if _KERNELS is None:
        from core.kernels.kernel_loader_v3 import load_kernel_stack
        _KERNELS = load_kernel_stack()
    return _KERNELS


def get_identity_profile() -> dict:
    return _get_kernels().get_kernel("identity") or {}


def apply_identity_to_response(text: str) -> str:
    identity = get_identity_profile()
    # Example: enforce tone, brevity, etc.
    style = identity.get("style", {})
    # You can later expand this; for now, just return text.
    return text
