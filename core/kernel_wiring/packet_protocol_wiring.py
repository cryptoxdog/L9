"""
10_packet_protocol_kernel → WS Router / Task Routing / EventStream

In orchestration/ws_task_router.py, runtime/websocket_orchestrator.py, or EventStream layer.
"""

_KERNELS = None


def _get_kernels():
    """Lazy load kernel stack."""
    global _KERNELS
    if _KERNELS is None:
        from core.kernels.kernel_loader_v3 import load_kernel_stack
        _KERNELS = load_kernel_stack()
    return _KERNELS


def get_packet_protocol() -> dict:
    return _get_kernels().get_kernel("packet_protocol") or {}


def get_allowed_event_types() -> list:
    return _get_kernels().get_rule(
        "packet_protocol", "events.allowed_types", default=[]
    ) or []


def get_default_channel() -> str:
    return _get_kernels().get_rule(
        "packet_protocol", "routing.default_channel", default="agent"
    )
