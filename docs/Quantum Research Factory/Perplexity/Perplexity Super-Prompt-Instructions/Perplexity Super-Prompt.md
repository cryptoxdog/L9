You are an applied research team tasked with deploying a multimodal AI autonomous agent on a VPS with tools and persistent state.

Your mission: design, implement, and document a **production-grade, reproducible, extensible system** with the following EXACT technology stack:

system_stack:
  framework: fastapi
  orchestration:
    primary: langgraph
    llm_abstraction: langchain
  models:
    llm_backend: openai_gpt4o
    multimodal: true
  persistence:
    postgres: long_term_memory
    pgvector: vector_embeddings
    redis: short_term_state
    redis_streams: event_bus
    filesystem: artifacts_and_logs
    minio: s3_storage
  tools:
    perception: vision_model_api
    http_requests: secure_async_http_client
    fs_access: sandboxed_fs
  security:
    auth: jwt
    sandbox: docker_sandbox
    secrets: env_vars
  observability:
    logging: structured_json
    metrics: prometheus
    tracing: minimal_local
  orchestration_core:
    task_queue: celery
    replication_engine: redis_streams
  runtime:
    realtime_output: sse
  ci_cd:
    automation: github_actions
  research:
    experiment_tracking: mlflow
  testing:
    framework: pytest
    async_support: pytest_asyncio
    migrations: alembic

Use this stack *as law*. No alternative libraries unless explicitly requested.

---------------------------------------------------------------------

## 1. System Overview

Build a **multimodal AI autonomous agent** running under FastAPI that:
- Accepts text + image input (OpenAI GPT-4o)
- Runs in Docker on a Linux VPS
- Uses LangGraph for orchestration and tool routing
- Stores long-term memory in Postgres (with pgvector)
- Uses Redis for short-term session state and Redis Streams for swarm messaging and replication
- Stores files in MinIO (S3-compatible)
- Emits metrics via Prometheus
- Streams agent output via SSE
- Executes code safely in Docker sandboxes
- Uses JWT auth
- Tracks experiments via MLflow
- Uses Celery for scheduling and distributed task execution
- Runs tests using pytest + pytest_asyncio
- Manages DB schema with Alembic
- Deploys via GitHub Actions

---------------------------------------------------------------------

## 2. Architecture Specification

### API Layer (FastAPI)
- Health, readiness, metrics
- Agent interaction (text + image upload)
- SSE streaming endpoint
- Admin endpoints behind JWT RBAC
- Pydantic input/output schemas

### Agent Orchestration Layer (LangGraph + LangChain)
- Planner + tool executor workflow
- Integrates:
  - LLM planning (GPT-4o)
  - Perception (image → analysis)
  - Tools (HTTP, FS sandbox, memory ops)
  - Short-term memory (Redis)
  - Long-term memory (PostgreSQL + pgvector)
- Graph nodes represent:
  - Plan
  - Route
  - Execute tool
  - Persist memory
  - Emit streaming output

### Persistence Layer
- PostgreSQL for durable memory, conversations, events
- pgvector for embedding-based retrieval
- Redis for in-session memory + shared state
- Redis Streams for swarm messaging + replication
- MinIO for files/artifacts/log dumps

### Tools
- Perception: GPT-4o image features/captions
- HTTP tool: aiohttp client wrapper
- FS tool: Docker sandbox execution
- Query tool: Postgres/pgvector search
- Memory tool: Redis (short-term), Postgres (long-term)

### Eventing & Distributed Components
- Celery task queue (agents can offload tasks)
- Redis Streams for:
  - Swarm coordination
  - Replication
  - Event log streaming
  - Multi-agent orchestration

### Security
- JWT auth
- Role-based access for admin routes
- Secrets via `.env`
- Docker sandbox:
  - Read-write restricted directories
  - Resource limits enabled

### Observability
- Structured JSON logs
- Prometheus metrics endpoint
- Latency histograms, agent step counters, tool call counters
- Minimal tracing hooks

---------------------------------------------------------------------

## 3. Implementation Deliverables

You must provide a **complete, self-contained bundle** with:

### Directory Layout
project/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── api/
│   ├── agent/
│   ├── models/
│   ├── tools/
│   ├── state/
│   ├── security/
│   ├── monitoring/
│   └── tasks/
├── scripts/
├── docker/
├── migrations/  # alembic
├── tests/
├── .env.example
├── docker-compose.yml
├── Dockerfile
└── README.md

### Required Code
- requirements.txt or pyproject.toml (pinned versions)
- FastAPI entrypoint
- LangGraph agent definition
- Tool registry + tool API wrappers
- Redis + Postgres repositories
- Alembic migrations
- Celery worker
- SSE streaming implementation
- MinIO S3 client wrapper
- Prometheus metrics collector
- JWT auth layer
- Docker sandbox executor

---------------------------------------------------------------------

## 4. Deployment Requirements

### MacOS Dev
- Install Python, Docker, Postgres/Redis/MinIO optional local
- Run migrations via Alembic
- Run dev server with uvicorn or docker-compose

### Ubuntu VPS
Provide instructions for:
- Docker install
- docker-compose up --build
- Environment file setup
- System-level firewall (port 80/443/8000)
- Reverse proxy via Nginx/Traefik
- TLS termination

---------------------------------------------------------------------

## 5. Testing Requirements

- pytest + pytest_asyncio for async agent tests
- Integration tests for LangGraph workflows
- Load tests optional
- Scripts to run:
  - Unit tests
  - Integration tests
  - Linting
  - Migrations

---------------------------------------------------------------------

## 6. Security Requirements
- JWT RBAC
- Directory sandboxing via Docker
- Secrets in `.env`
- Least privilege FS access
- Strong secret key generation

---------------------------------------------------------------------

## 7. Reproducibility Requirements
- Fully documented `.env.example`
- All model configs explicit
- One-command build + run
- One-command test suite execution
- Deployment checklist

---------------------------------------------------------------------

## 8. Documentation Requirements
Produce clear technical docs covering:
- Architecture  
- Installation  
- Config  
- Tools  
- Memory  
- Replication  
- Deployment  
- Testing  
- Security  
- Observability  

---------------------------------------------------------------------

## 9. Internal Design Comparison Table
Include a table comparing design decisions but base final choices strictly on the confirmed stack.

---------------------------------------------------------------------

## 10. Final Output
A **single response** containing:
- Architecture  
- Code  
- Configs  
- Deployment scripts  
- Testing scripts  
- Security documentation  
- Observability instrumentation  

Everything must be **copy/paste runnable**, self-contained, and deployable on a VPS.

