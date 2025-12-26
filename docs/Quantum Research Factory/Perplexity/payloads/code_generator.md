# PERPLEXITY PAYLOAD: Code Generator (Phase 2)

Use this AFTER you have a spec. Paste the spec below and get Python code back.

Copy everything below this line and paste into Perplexity Labs:

---

You are a senior L9 Python engineer. Generate **production-ready Python code** from the Module Spec below.

## MODULE SPEC

```yaml
# PASTE YOUR MODULE SPEC HERE
```

## CODE GENERATION REQUIREMENTS

Generate the following files as separate code blocks, each labeled with the filename:

### 1. `api/adapters/{module}_adapter.py`
- Main adapter class with FastAPI route handlers
- HMAC signature verification (if applicable)
- PacketEnvelope creation with proper metadata
- Dependency injection for services
- Proper error handling per error_policy

### 2. `api/routes/{module}.py`  
- FastAPI APIRouter with prefix
- Route registration
- Request/response Pydantic models
- OpenAPI documentation

### 3. `{module}_client.py` (if outbound calls needed)
- httpx async client
- Timeout and retry logic per spec
- Response parsing

### 4. `tests/test_{module}_adapter.py`
- pytest async tests
- Cover all acceptance.positive cases
- Mock external dependencies
- Test idempotency

### 5. `tests/test_{module}_smoke.py` (if docker_smoke: true)
- Docker integration test
- Real HTTP calls to running container
- Health check verification

## L9 CODE STANDARDS

```python
# Required imports
from structlog import get_logger
import httpx
from core.packet_protocol import PacketEnvelopeIn, create_packet
from core.substrate_service import SubstrateService

# Logging (NEVER use print or logging)
logger = get_logger(__name__)

# HTTP client (NEVER use requests or aiohttp)
async with httpx.AsyncClient(timeout=30.0) as client:
    response = await client.post(...)

# Dependency injection pattern
async def handle_webhook(
    request: Request,
    substrate: SubstrateService = Depends(get_substrate),
):
    ...

# Thread UUID (use UUIDv5, not uuid4)
import uuid
thread_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"{source}:{identifier}")
```

## OUTPUT FORMAT

Label each file clearly:

```python
# === FILE: api/adapters/slack_adapter.py ===
...code...
```

```python
# === FILE: api/routes/slack.py ===
...code...
```

Generate complete, runnable code. No placeholders. No `# TODO` comments.

