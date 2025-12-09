"""
L9 Runtime Startup — Kernel Stack Accessor

Provides centralized access to the loaded KernelStack.
"""

from core.kernels.kernel_loader_v3 import load_kernel_stack

KERNEL_STACK = load_kernel_stack()


def get_kernel_stack():
    """
    Global accessor for the loaded KernelStack.

    We keep this as a thin wrapper so tests can monkeypatch it.
    """
    return KERNEL_STACK

