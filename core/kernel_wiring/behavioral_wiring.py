"""
04_behavioral_kernel → Prohibitions / Output Defaults

Anywhere you enforce behavior (e.g. controlling verbosity, humor, filters).
"""

_KERNELS = None


def _get_kernels():
    """Lazy load kernel stack."""
    global _KERNELS
    if _KERNELS is None:
        from runtime.kernel_loader import load_kernel_stack

        _KERNELS = load_kernel_stack()
    return _KERNELS


def get_output_verbosity() -> str:
    return _get_kernels().get_rule(
        "behavioral",
        "output.verbosity",
        default="minimal",
    )


def is_topic_blocked(topic: str) -> bool:
    blocked = (
        _get_kernels().get_rule("behavioral", "prohibited_topics", default=[]) or []
    )
    return topic in blocked
