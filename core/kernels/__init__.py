"""
L9 Core Kernels Module
======================

Kernel integrity verification.

Note: Kernel loading functions have been consolidated into runtime.kernel_loader.
This module re-exports them for backward compatibility.

Components:
- integrity: Hash-based tamper detection
- runtime.kernel_loader: YAML kernel loading (canonical location)

Version: 1.1.0
"""

import warnings

from core.kernels.integrity import (
    hash_file,
    compute_kernel_hashes,
    load_kernel_hashes,
    save_kernel_hashes,
    check_kernel_integrity,
    get_detailed_changes,
    verify_specific_file,
    initialize_kernel_hashes,
    IntegrityChange,
    KERNEL_HASH_FILE,
)

# Re-export from canonical location (runtime.kernel_loader)
# Backward compatibility for code using core.kernels.private_loader
from runtime.kernel_loader import (
    load_kernel_file,
    load_all_private_kernels,
    load_layered_kernels,
    get_kernel_by_name,
    get_enabled_rules,
    get_rules_by_type,
    validate_kernel_structure,
    validate_all_kernels,
    DEFAULT_KERNEL_PATH,
    KERNEL_EXTENSIONS,
)

# Emit deprecation warning when accessing via this module
def __getattr__(name: str):
    if name in (
        "load_kernel_file", "load_all_private_kernels", "load_layered_kernels",
        "get_kernel_by_name", "get_enabled_rules", "get_rules_by_type",
        "validate_kernel_structure", "validate_all_kernels",
    ):
        warnings.warn(
            f"core.kernels.{name} is deprecated. Use runtime.kernel_loader.{name} instead.",
            DeprecationWarning,
            stacklevel=2,
        )
    raise AttributeError(f"module 'core.kernels' has no attribute '{name}'")

__all__ = [
    # Integrity
    "hash_file",
    "compute_kernel_hashes",
    "load_kernel_hashes",
    "save_kernel_hashes",
    "check_kernel_integrity",
    "get_detailed_changes",
    "verify_specific_file",
    "initialize_kernel_hashes",
    "IntegrityChange",
    "KERNEL_HASH_FILE",
    # Private Loader
    "load_kernel_file",
    "load_all_private_kernels",
    "load_layered_kernels",
    "get_kernel_by_name",
    "get_enabled_rules",
    "get_rules_by_type",
    "validate_kernel_structure",
    "validate_all_kernels",
    "DEFAULT_KERNEL_PATH",
    "KERNEL_EXTENSIONS",
]

