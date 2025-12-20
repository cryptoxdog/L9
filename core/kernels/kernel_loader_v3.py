"""
L9 Kernel Loader v3 - DEPRECATED

⚠️  DEPRECATED: Use runtime.kernel_loader instead.

This module now re-exports from runtime.kernel_loader for backward compatibility.
All new code should import directly from runtime.kernel_loader.

Migration:
    # OLD (deprecated)
    from core.kernels.kernel_loader_v3 import load_kernel_stack, KernelStack
    
    # NEW (use this)
    from runtime.kernel_loader import load_kernel_stack, KernelStack
"""

import warnings
from runtime.kernel_loader import (
    load_kernel_stack,
    KernelStack,
    KERNEL_ID_MAP,
)

# Emit deprecation warning on import
warnings.warn(
    "core.kernels.kernel_loader_v3 is deprecated. "
    "Use runtime.kernel_loader instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Legacy aliases for backward compatibility
KERNEL_SEQUENCE = [
    {"id": kid, "file": fname}
    for kid, fname in KERNEL_ID_MAP.items()
]

DEFAULT_KERNEL_BASE = None  # Now determined dynamically in runtime.kernel_loader

__all__ = [
    "load_kernel_stack",
    "KernelStack",
    "KERNEL_SEQUENCE",
    "DEFAULT_KERNEL_BASE",
]

