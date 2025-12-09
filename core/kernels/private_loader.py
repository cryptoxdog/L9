"""
L9 Core Kernels - Private Loader
================================

Loads private kernel YAML files with integrity verification.

Features:
- Automatic integrity checking on load
- Priority-based kernel ordering
- Tamper detection with configurable response
- Support for kernel inheritance and composition

Usage:
    from core.kernels.private_loader import load_all_private_kernels
    
    kernels = load_all_private_kernels("l9_private")
    for kernel in kernels:
        print(kernel["kernel"]["name"])

Version: 1.0.0
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from core.kernels.integrity import check_kernel_integrity, IntegrityChange

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

DEFAULT_KERNEL_PATH = "l9_private"
KERNEL_EXTENSIONS = (".yaml", ".yml")


# =============================================================================
# Kernel Loading
# =============================================================================

def load_kernel_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Load a single kernel YAML file.
    
    Args:
        file_path: Path to kernel file
        
    Returns:
        Parsed kernel dict, or None on failure
    """
    try:
        with open(file_path, "r") as f:
            content = yaml.safe_load(f)
            
        if content is None:
            logger.warning(f"Empty kernel file: {file_path}")
            return None
            
        # Add file metadata
        content["_source_file"] = str(file_path)
        
        return content
        
    except yaml.YAMLError as e:
        logger.error(f"YAML parse error in {file_path}: {e}")
        return None
    except (IOError, OSError) as e:
        logger.error(f"Failed to read {file_path}: {e}")
        return None


def load_all_private_kernels(
    base_path: str = DEFAULT_KERNEL_PATH,
    check_integrity: bool = True,
    fail_on_tamper: bool = False,
) -> List[Dict[str, Any]]:
    """
    Load all private kernel YAML files from a directory.

    Updated behavior:
        - Supports layered layout under base_path:
              base_path/
                kernels/
                  00_system/
                  10_cognitive_v2/
                  90_project/
        - If the layered layout exists, loads in layer order:
              00_system -> 10_cognitive_v2 (optional) -> 90_project
        - If layered layout does NOT exist, falls back to previous
          behavior: rglob all YAMLs under base_path.
        - Still supports integrity checking via check_kernel_integrity.

    Args:
        base_path: Base directory to scan for kernels (e.g. "l9_private")
        check_integrity: Whether to verify file integrity
        fail_on_tamper: Whether to raise error on tampered files

    Returns:
        List of kernel dicts, sorted by (layer_order, kernel.priority)
    """
    base = Path(base_path)

    if not base.exists():
        logger.warning(f"Kernel base path does not exist: {base_path}")
        return []

    # Integrity check is done on the original base path to preserve
    # existing behavior and hash file location.
    if check_integrity:
        changes = check_kernel_integrity(base_path)
        if changes:
            modified = [p for p, c in changes.items() if c == IntegrityChange.MODIFIED]
            if modified:
                logger.warning(f"Kernel integrity changes detected: {changes}")

                if fail_on_tamper:
                    raise RuntimeError(
                        f"Kernel tampering detected in files: {modified}. "
                        "Aborting load for security."
                    )

    # Determine where kernel files live:
    #   - If base/kernels/ exists, use that as root
    #   - Otherwise, use base itself (old behavior)
    kernel_root = base / "kernels"
    if not kernel_root.exists():
        kernel_root = base

    # Layer configuration: lower order = earlier load.
    # NOTE: Layers are optional. If a directory doesn't exist, it's skipped.
    LAYER_DEFS = [
        ("00_system", 0),
        ("10_cognitive_v2", 10),
        ("90_project", 90),
    ]

    # v2 kernels always enabled (no env flag needed)
    layer_dirs: List[tuple[Path, int, str]] = []
    for name, order in LAYER_DEFS:
        layer_path = kernel_root / name
        if layer_path.exists() and layer_path.is_dir():
            layer_dirs.append((layer_path, order, name))

    use_layered = len(layer_dirs) > 0

    kernels: List[Dict[str, Any]] = []

    if use_layered:
        # Layered mode: iterate layers in order and tag each kernel with layer metadata
        layer_dirs.sort(key=lambda t: t[1])

        for ext in KERNEL_EXTENSIONS:
            for layer_path, order, layer_name in layer_dirs:
                for file in layer_path.rglob(f"*{ext}"):
                    kernel = load_kernel_file(file)
                    if kernel:
                        # Tag layer metadata for sorting/auditing
                        kernel.setdefault("_meta", {})
                        kernel["_meta"]["source_file"] = str(file)
                        kernel["_meta"]["layer"] = layer_name
                        kernel["_meta"]["layer_order"] = order
                        kernels.append(kernel)
    else:
        # Fallback: original behavior (flat scan under kernel_root)
        for ext in KERNEL_EXTENSIONS:
            for file in kernel_root.rglob(f"*{ext}"):
                kernel = load_kernel_file(file)
                if kernel:
                    kernels.append(kernel)

    # Sort kernels by (layer_order, kernel.priority)
    def _sort_key(k: Dict[str, Any]) -> tuple[int, int]:
        layer_order = 50
        meta = k.get("_meta") or {}
        if isinstance(meta, dict):
            layer_order = int(meta.get("layer_order", 50))

        kernel_info = k.get("kernel", {}) or {}
        priority = int(kernel_info.get("priority", 100))
        return (layer_order, priority)

    kernels.sort(key=_sort_key)

    logger.info(
        f"Loaded {len(kernels)} private kernels from {kernel_root} "
        f"(base_path={base_path}, layered={use_layered})"
    )

    return kernels


def get_kernel_by_name(
    name: str,
    base_path: str = DEFAULT_KERNEL_PATH,
) -> Optional[Dict[str, Any]]:
    """
    Get a specific kernel by name.
    
    Args:
        name: Kernel name to find
        base_path: Base directory to search
        
    Returns:
        Kernel dict if found, None otherwise
    """
    kernels = load_all_private_kernels(base_path, check_integrity=False)
    
    for kernel in kernels:
        kernel_info = kernel.get("kernel", {})
        if kernel_info.get("name") == name:
            return kernel
    
    return None


def get_enabled_rules(
    base_path: str = DEFAULT_KERNEL_PATH,
) -> List[Dict[str, Any]]:
    """
    Get all enabled rules from all kernels.
    
    Rules are returned sorted by kernel priority and rule order.
    
    Args:
        base_path: Base directory to search
        
    Returns:
        List of enabled rule dicts
    """
    kernels = load_all_private_kernels(base_path)
    rules: List[Dict[str, Any]] = []
    
    for kernel in kernels:
        kernel_info = kernel.get("kernel", {})
        kernel_name = kernel_info.get("name", "unknown")
        kernel_priority = kernel_info.get("priority", 100)
        
        for rule in kernel_info.get("rules", []):
            if rule.get("enabled", True):
                # Enrich rule with kernel context
                enriched = {
                    **rule,
                    "_kernel_name": kernel_name,
                    "_kernel_priority": kernel_priority,
                }
                rules.append(enriched)
    
    return rules


def get_rules_by_type(
    rule_type: str,
    base_path: str = DEFAULT_KERNEL_PATH,
) -> List[Dict[str, Any]]:
    """
    Get all enabled rules of a specific type.
    
    Args:
        rule_type: Type of rules to get (e.g., "capability", "safety")
        base_path: Base directory to search
        
    Returns:
        List of matching rule dicts
    """
    all_rules = get_enabled_rules(base_path)
    return [r for r in all_rules if r.get("type") == rule_type]


# =============================================================================
# Kernel Validation
# =============================================================================

def validate_kernel_structure(kernel: Dict[str, Any]) -> List[str]:
    """
    Validate kernel structure against expected schema.
    
    Args:
        kernel: Kernel dict to validate
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors: List[str] = []
    
    # Must have kernel key
    if "kernel" not in kernel:
        errors.append("Missing 'kernel' key")
        return errors
    
    kernel_info = kernel["kernel"]
    
    # Required fields
    required = ["name", "version"]
    for field in required:
        if field not in kernel_info:
            errors.append(f"Missing required field: kernel.{field}")
    
    # Validate rules if present
    rules = kernel_info.get("rules", [])
    if not isinstance(rules, list):
        errors.append("kernel.rules must be a list")
    else:
        for i, rule in enumerate(rules):
            if not isinstance(rule, dict):
                errors.append(f"Rule {i} must be a dict")
                continue
            if "id" not in rule:
                errors.append(f"Rule {i} missing 'id' field")
            if "type" not in rule:
                errors.append(f"Rule {i} missing 'type' field")
    
    return errors


def validate_all_kernels(base_path: str = DEFAULT_KERNEL_PATH) -> Dict[str, List[str]]:
    """
    Validate all kernels in a directory.
    
    Args:
        base_path: Base directory to scan
        
    Returns:
        Dict mapping file paths to list of validation errors
    """
    base = Path(base_path)
    results: Dict[str, List[str]] = {}
    
    for ext in KERNEL_EXTENSIONS:
        for file in base.rglob(f"*{ext}"):
            kernel = load_kernel_file(file)
            if kernel:
                errors = validate_kernel_structure(kernel)
                if errors:
                    results[str(file)] = errors
    
    return results


# =============================================================================
# Convenience Aliases
# =============================================================================

def load_layered_kernels(
    base_path: str = DEFAULT_KERNEL_PATH,
    check_integrity: bool = False,
) -> List[Dict[str, Any]]:
    """
    Convenience alias for load_all_private_kernels with v2 always enabled.
    
    Loads kernels in deterministic layer order:
        1) 00_system (core system kernels)
        2) 10_cognitive_v2 (v2 cognitive engines)
        3) 90_project (project-specific kernels)
    
    Args:
        base_path: Base directory to scan for kernels
        check_integrity: Whether to verify file integrity
        
    Returns:
        List of kernel dicts with _meta.layer and _meta.source_file attached
    """
    return load_all_private_kernels(base_path, check_integrity=check_integrity)


# =============================================================================
# Public API
# =============================================================================

__all__ = [
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

