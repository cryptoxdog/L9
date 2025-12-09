"""
L9 Kernel Loader v3 (Deterministic)

- Loads the 10 consolidated kernels from 00_system/ in a fixed sequence.
- Computes per-file hashes for drift detection.
- Exposes a simple KernelStack context for runtime consumers.
- Does NOT rename or depend on any existing env vars.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


# Base directory for the 10-kernel stack.
# Adjusted for L9 repo layout: core/kernels/ -> l9_private/kernels/00_system/
DEFAULT_KERNEL_BASE = Path(__file__).resolve().parents[2] / "l9_private" / "kernels" / "00_system"


# Explicit sequence, matching your consolidated structure.
KERNEL_SEQUENCE: List[Dict[str, str]] = [
    {"id": "master",        "file": "01_master_kernel.yaml"},
    {"id": "identity",      "file": "02_identity_kernel.yaml"},
    {"id": "cognitive",     "file": "03_cognitive_kernel.yaml"},
    {"id": "behavioral",    "file": "04_behavioral_kernel.yaml"},
    {"id": "memory",        "file": "05_memory_kernel.yaml"},
    {"id": "worldmodel",    "file": "06_worldmodel_kernel.yaml"},
    {"id": "execution",     "file": "07_execution_kernel.yaml"},
    {"id": "safety",        "file": "08_safety_kernel.yaml"},
    {"id": "developer",     "file": "09_developer_kernel.yaml"},
    {"id": "packet_protocol", "file": "10_packet_protocol_kernel.yaml"},
]


class KernelStack:
    """
    Lightweight context object for the 10-kernel stack.

    - kernels_by_id:  id -> parsed YAML dict
    - kernels_by_file: filename -> parsed YAML dict
    - hashes: filename -> sha256 hex digest
    - metadata: free-form (e.g. load time, base_dir)
    """

    def __init__(
        self,
        kernels_by_id: Dict[str, Dict[str, Any]],
        kernels_by_file: Dict[str, Dict[str, Any]],
        hashes: Dict[str, str],
        base_dir: Path,
    ) -> None:
        self.kernels_by_id = kernels_by_id
        self.kernels_by_file = kernels_by_file
        self.hashes = hashes
        self.base_dir = base_dir

    def get_kernel(self, kernel_id: str) -> Optional[Dict[str, Any]]:
        return self.kernels_by_id.get(kernel_id)

    def get_hash(self, filename: str) -> Optional[str]:
        return self.hashes.get(filename)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "kernels_by_id": self.kernels_by_id,
            "kernels_by_file": self.kernels_by_file,
            "hashes": self.hashes,
            "base_dir": str(self.base_dir),
        }

    def get_rule(self, kernel_id: str, path: str, default: Any = None) -> Any:
        """
        Convenience accessor.

        Example:
            get_rule("cognitive", "reasoning.modes.default") ->
                kernels_by_id["cognitive"]["reasoning"]["modes"]["default"]
        """
        root = self.kernels_by_id.get(kernel_id)
        if root is None:
            return default

        node: Any = root
        for part in path.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node


def _load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _sha256_of_file(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha256(data).hexdigest()


def load_kernel_stack(
    base_dir: Optional[Path] = None,
) -> KernelStack:
    """
    Deterministically load the 10 consolidated kernels from 00_system/.

    - Uses explicit KERNEL_SEQUENCE order.
    - Fails fast if a listed file is missing.
    - Computes sha256 for each file for drift detection.
    - Returns KernelStack context.

    Does NOT modify any global state.
    """
    if base_dir is None:
        base_dir = DEFAULT_KERNEL_BASE

    kernels_by_id: Dict[str, Dict[str, Any]] = {}
    kernels_by_file: Dict[str, Dict[str, Any]] = {}
    hashes: Dict[str, str] = {}

    for entry in KERNEL_SEQUENCE:
        kernel_id = entry["id"]
        filename = entry["file"]
        full_path = base_dir / filename

        if not full_path.exists():
            raise FileNotFoundError(
                f"Kernel file missing: {full_path} (id={kernel_id})"
            )

        data = _load_yaml(full_path)
        digest = _sha256_of_file(full_path)

        kernels_by_id[kernel_id] = data
        kernels_by_file[filename] = data
        hashes[filename] = digest

    return KernelStack(
        kernels_by_id=kernels_by_id,
        kernels_by_file=kernels_by_file,
        hashes=hashes,
        base_dir=base_dir,
    )

