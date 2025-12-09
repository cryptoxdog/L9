### A. Kernel Loader v3 (Deterministic Loader for 10 Kernels)

Drop this in as a **new file** so we don’t break anything existing, e.g.:

`core/kernels/kernel_loader_v3.py`
(adjust path to match your repo layout; names stay neutral and non-invasive)

```python
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
# Adjust if 00_system lives somewhere else relative to this file.
DEFAULT_KERNEL_BASE = Path(__file__).resolve().parents[2] / "00_system"


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
```

This file:

* **Does not rename anything in your repo.**
* **Does not touch env vars.**
* **Only knows about `00_system/01–10` and returns a clean context.**

You (or Cursor) can now import `load_kernel_stack()` anywhere without breaking old behavior.

---

### B. Runtime Wiring for the 10 Kernels

Now we hook that loader into the runtime **without** refactors. Just wiring.

Think of it as: *everyone gets a `kernel_ctx` injection and uses `get_rule()` instead of hardcoded constants.*

#### 1. Centralize kernel context in startup/boot

In whatever your main startup path is (e.g. `runtime/startup.py` or `api/main.py`), add:

```python
# runtime/startup.py (or equivalent)

from core.kernels.kernel_loader_v3 import load_kernel_stack

KERNEL_STACK = load_kernel_stack()


def get_kernel_stack():
    """
    Global accessor for the loaded KernelStack.

    We keep this as a thin wrapper so tests can monkeypatch it.
    """
    return KERNEL_STACK
```

That’s it. No behavior change yet.

---

#### 2. Wire each kernel to its main consumer(s)

Below is a **wiring map** plus concrete code snippets you can drop into the relevant modules.

##### 01_master_kernel → Orchestrator / Global Behavior

Use it in your orchestrator (e.g. `orchestration/orchestrator.py`) to get top-level flags like modes, drift rules, etc.

```python
# at top of orchestrator.py
from runtime.startup import get_kernel_stack

KERNELS = get_kernel_stack()

def get_active_mode() -> str:
    mode = KERNELS.get_rule("master", "modes.default", default="Developer_Mode")
    return mode
```

Anywhere you previously hardcoded “modes” or global behavior, replace with `get_rule("master", ...)`.

---

##### 02_identity_kernel → Output Formatting / Persona

In your main response / formatting layer (wherever you shape responses; e.g. `orchestration/unified_controller.py` or `agent/architect.py`):

```python
from runtime.startup import get_kernel_stack

KERNELS = get_kernel_stack()

def get_identity_profile() -> dict:
    return KERNELS.get_kernel("identity") or {}


def apply_identity_to_response(text: str) -> str:
    identity = get_identity_profile()
    # Example: enforce tone, brevity, etc.
    style = identity.get("style", {})
    # You can later expand this; for now, just return text.
    return text
```

Use this in the final response step to apply tone/structure rules if you want.

---

##### 03_cognitive_kernel → Reasoning / Meta-cognition

Where your “reasoning engine” or planner lives (`modules/ir_engine/`, planning modules, etc.):

```python
from runtime.startup import get_kernel_stack

KERNELS = get_kernel_stack()

def get_reasoning_mode() -> str:
    return KERNELS.get_rule(
        "cognitive",
        "reasoning.default_mode",
        default="fast_chain",
    )


def should_enable_meta_cognition() -> bool:
    return bool(
        KERNELS.get_rule("cognitive", "metacognition.enabled", default=False)
    )
```

Use these in your IR/planning engine to choose reasoning styles without hardcoding.

---

##### 04_behavioral_kernel → Prohibitions / Output Defaults

Anywhere you enforce behavior (e.g. controlling verbosity, humor, filters; likely in unified controller):

```python
from runtime.startup import get_kernel_stack

KERNELS = get_kernel_stack()


def get_output_verbosity() -> str:
    return KERNELS.get_rule(
        "behavioral",
        "output.verbosity",
        default="minimal",
    )


def is_topic_blocked(topic: str) -> bool:
    blocked = KERNELS.get_rule("behavioral", "prohibited_topics", default=[]) or []
    return topic in blocked
```

---

##### 05_memory_kernel → Memory Adapter / Substrate Client

In `memory/memory_client.py` or similar:

```python
from runtime.startup import get_kernel_stack

KERNELS = get_kernel_stack()


def get_memory_layers_config() -> dict:
    return KERNELS.get_rule("memory", "layers", default={}) or {}


def should_checkpoint_now(event_type: str) -> bool:
    rules = KERNELS.get_rule("memory", "checkpointing.triggers", default=[]) or []
    return event_type in rules
```

Use this for deciding when to write, what layers to hit, etc.

---

##### 06_worldmodel_kernel → World Model / Entity Graph

In `world_model/repository.py` or `world_model/*`:

```python
from runtime.startup import get_kernel_stack

KERNELS = get_kernel_stack()


def get_worldmodel_schema() -> dict:
    return KERNELS.get_kernel("worldmodel") or {}
```

You can then apply schema rules to ensure you’re writing consistent entity types, relations, etc.

---

##### 07_execution_kernel → Execution Engine / State Machine

In your execution engine module (or where you plan to put it), something like `orchestration/execution_engine.py`:

```python
from runtime.startup import get_kernel_stack

KERNELS = get_kernel_stack()


def get_execution_state_machine() -> dict:
    return KERNELS.get_kernel("execution") or {}


def get_allowed_transitions(state: str) -> list[str]:
    sm = get_execution_state_machine()
    transitions = sm.get("transitions", {})
    return transitions.get(state, [])
```

Use this to drive which steps the orchestrator is allowed to take (e.g., PLAN → EXECUTE → VERIFY).

---

##### 08_safety_kernel → Safety Scanners / Guardrails

In your safety layer (`modules/safety/` or preflight hooks), e.g. `modules/safety/guardrail.py`:

```python
from runtime.startup import get_kernel_stack

KERNELS = get_kernel_stack()


def get_safety_policies() -> dict:
    return KERNELS.get_kernel("safety") or {}


def is_destructive_action(action: str) -> bool:
    destructive = KERNELS.get_rule("safety", "destructive.actions", default=[]) or []
    return action in destructive
```

Use before destructive ops (file write, system commands, external calls).

---

##### 09_developer_kernel → Engineering Governance

In dev-only or spec/validation modules, e.g. `dev/spec_enforcer.py`:

```python
from runtime.startup import get_kernel_stack

KERNELS = get_kernel_stack()


def get_dev_policies() -> dict:
    return KERNELS.get_kernel("developer") or {}
```

Use this to enforce “spec-first” rules, test expectations, CI behavior, etc.

---

##### 10_packet_protocol_kernel → WS Router / Task Routing / EventStream

In `orchestration/ws_task_router.py`, `runtime/websocket_orchestrator.py`, or your EventStream layer:

```python
from runtime.startup import get_kernel_stack

KERNELS = get_kernel_stack()


def get_packet_protocol() -> dict:
    return KERNELS.get_kernel("packet_protocol") or {}


def get_allowed_event_types() -> list[str]:
    return KERNELS.get_rule(
        "packet_protocol", "events.allowed_types", default=[]
    ) or []


def get_default_channel() -> str:
    return KERNELS.get_rule(
        "packet_protocol", "routing.default_channel", default="agent"
    )
```
