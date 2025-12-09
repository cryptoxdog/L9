# L9 Kernel Loading Model – v2 Enabled by Default

L9 loads kernels in **three deterministic layers**:

## Layer Order

| Layer | Directory | Purpose |
|-------|-----------|---------|
| 0 | `l9_private/kernels/00_system/` | Core system kernels (always loaded first) |
| 10 | `l9_private/kernels/10_cognitive_v2/` | v2 cognitive engines (always enabled) |
| 90 | `l9_private/kernels/90_project/` | Project-specific kernels |

## 1. System Layer (00_system)

**Location:** `l9_private/kernels/00_system/`

Core system kernels that define L9's foundational behavior:

- `00_master_kernel.yaml`
- `01_memory_kernel.yaml`
- `02_cognitive_kernel.yaml`
- `03_behavioral_kernel.yaml`
- `04_packet_protocol.yaml`
- `05_developer_mode.yaml`

## 2. v2 Cognitive Layer (10_cognitive_v2)

**Location:** `l9_private/kernels/10_cognitive_v2/`

Advanced cognitive engines (always enabled, no env flag required):

- `00_context_engine_v2.yaml`
- `01_reasoning_engine_v2.yaml`
- `02_worldmodel_engine_v2.yaml`
- `03_identity_personality_v2.yaml`

## 3. Project Layer (90_project)

**Location:** `l9_private/kernels/90_project/`

Optional project-specific kernel overrides and extensions.

## Metadata

Each loaded kernel includes audit metadata:

```yaml
_meta:
  source_file: "l9_private/kernels/00_system/00_master_kernel.yaml"
  layer: "00_system"
  layer_order: 0
```

## API Usage

```python
from core.kernels import load_layered_kernels, load_all_private_kernels

# Primary API - loads all kernels in layer order
kernels = load_layered_kernels()

# With integrity checking
kernels = load_all_private_kernels(check_integrity=True)
```

## Integrity

L9 computes per-file SHA256 hashes stored in `l9_private/kernel_hashes.json`:

- **NEW**: File not in stored hashes
- **MODIFIED**: Hash mismatch detected
- **DELETED**: File removed from disk

## Guarantees

- **Deterministic**: Same input → same load order
- **Stable**: No external env flags required
- **Testable**: Predictable behavior in tests
- **Auditable**: Full metadata trail per kernel

