# L9 Development Memos

## Open Items

### Python Version Compatibility Check
- **File:** `memory/substrate_graph.py`
- **Issue:** Added `from __future__ import annotations` for Python 3.9 compatibility on local dev machine
- **Context:** Repo requires Python ≥3.12 (`pyproject.toml`), but local Mac runs 3.9.6
- **Action needed:** Decide whether to keep the `__future__` import (harmless) or remove it (not needed for production)
- **Added:** 2025-12-26

