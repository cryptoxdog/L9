"""
06_worldmodel_kernel → World Model / Entity Graph

In world_model/repository.py or world_model/*.
"""

_KERNELS = None


def _get_kernels():
    """Lazy load kernel stack."""
    global _KERNELS
    if _KERNELS is None:
        from core.kernels.kernel_loader_v3 import load_kernel_stack
        _KERNELS = load_kernel_stack()
    return _KERNELS


def get_worldmodel_schema() -> dict:
    return _get_kernels().get_kernel("worldmodel") or {}
