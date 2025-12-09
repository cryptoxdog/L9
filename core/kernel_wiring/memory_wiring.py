"""
05_memory_kernel → Memory Adapter / Substrate Client

In memory/memory_client.py or similar.
"""

_KERNELS = None


def _get_kernels():
    """Lazy load kernel stack."""
    global _KERNELS
    if _KERNELS is None:
        from core.kernels.kernel_loader_v3 import load_kernel_stack
        _KERNELS = load_kernel_stack()
    return _KERNELS


def get_memory_layers_config() -> dict:
    return _get_kernels().get_rule("memory", "layers", default={}) or {}


def should_checkpoint_now(event_type: str) -> bool:
    rules = _get_kernels().get_rule("memory", "checkpointing.triggers", default=[]) or []
    return event_type in rules
