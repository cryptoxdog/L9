# L9 PRIVATE_BOUNDARY Specification

## Overview

This document defines the information boundary for L9 orchestration.
Information crossing this boundary is subject to enforcement rules.

## Boundary Rules

### Phase 1 (Current - Stub Implementation)

Default patterns for automatic redaction:
- API keys and secrets (pattern: `api_key=...`, `secret=...`)
- Password fields (pattern: `password=...`)
- Token values (pattern: `token=...`)

### Phase 2 (Planned)

Full boundary enforcement with:
- Domain-specific redaction rules
- Field-level protection in payloads
- Context-aware enforcement

## Protected Information Classes

| Class | Description | Action |
|-------|-------------|--------|
| credentials | API keys, passwords, tokens | REDACT |
| pii | Personal identifiable information | REDACT |
| internal_paths | Internal file paths | MASK |
| debug_info | Stack traces, debug output | FILTER |

## Configuration

Boundary enforcement is configured in `l9_private/security/l9_security_kernel.yaml`.

## Usage

```python
from core.boundary import enforce_boundary

# Apply boundary enforcement to prompts
safe_prompt = enforce_boundary(raw_prompt)

# Apply to responses
safe_response = enforce_response_boundary(raw_response)
```

---
Version: 1.0.0
Last Updated: 2024-12-08

