"""
L9 Core Kernels Module
======================

Kernel integrity verification and private kernel loading.

Components:
- integrity: Hash-based tamper detection
- private_loader: YAML kernel loading with validation

Version: 1.0.0
"""

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

from core.kernels.private_loader import (
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

