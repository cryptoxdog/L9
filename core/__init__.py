"""
L9 Core Module
==============

Core infrastructure for L9 orchestration system.

Submodules:
- schemas: Pydantic models for packets, research, security
- retrievers: Memory substrate retrievers
- kernels: Kernel integrity and loading
- boundary: PRIVATE_BOUNDARY enforcement

Version: 2.1.0
"""

# Note: Submodules are imported on-demand to avoid circular imports
# Use explicit imports:
#   from core.schemas import PacketEnvelope
#   from core.kernels import check_kernel_integrity
#   from core.boundary import enforce_boundary

__version__ = "2.1.0"
