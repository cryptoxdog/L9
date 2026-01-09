"""
L9 Core - Module Registry
========================

Runtime registry for "what modules exist, what they expose, and whether they're active/healthy".

This is NOT the YAML `specs/MODULE_REGISTRY.yaml` (which is a design/spec artifact).
This registry is runtime truth derived from server wiring and health checks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import structlog

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class ModuleDefinition:
    module_id: str
    display_name: str
    route_prefix: Optional[str] = None
    owner: Optional[str] = None
    version: Optional[str] = None
    required_env: tuple[str, ...] = ()


@dataclass(frozen=True)
class ModuleStatus:
    module_id: str
    enabled: bool
    available: bool
    initialized: bool
    notes: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ModuleRegistry:
    """
    In-memory module registry (runtime truth).

    - register(): declare module existence (and metadata)
    - set_status(): update current runtime status
    - snapshot(): deterministic, JSON-ready view
    """

    def __init__(self) -> None:
        self._definitions: dict[str, ModuleDefinition] = {}
        self._status: dict[str, ModuleStatus] = {}
        logger.info("ModuleRegistry initialized")

    def register(self, definition: ModuleDefinition) -> None:
        self._definitions[definition.module_id] = definition

    def set_status(self, status: ModuleStatus) -> None:
        self._status[status.module_id] = status

    def get_definition(self, module_id: str) -> Optional[ModuleDefinition]:
        return self._definitions.get(module_id)

    def get_status(self, module_id: str) -> Optional[ModuleStatus]:
        return self._status.get(module_id)

    def snapshot(self) -> dict[str, Any]:
        """
        Return a deterministic snapshot (sorted by module_id).
        """
        module_ids = sorted(set(self._definitions.keys()) | set(self._status.keys()))
        modules: list[dict[str, Any]] = []

        for module_id in module_ids:
            definition = self._definitions.get(module_id)
            status = self._status.get(module_id)

            modules.append(
                {
                    "module_id": module_id,
                    "definition": None
                    if definition is None
                    else {
                        "display_name": definition.display_name,
                        "route_prefix": definition.route_prefix,
                        "owner": definition.owner,
                        "version": definition.version,
                        "required_env": list(definition.required_env),
                    },
                    "status": None
                    if status is None
                    else {
                        "enabled": status.enabled,
                        "available": status.available,
                        "initialized": status.initialized,
                        "notes": status.notes,
                        "metadata": status.metadata,
                    },
                }
            )

        return {"count": len(modules), "modules": modules}


