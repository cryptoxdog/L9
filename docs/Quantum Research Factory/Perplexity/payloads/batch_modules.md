# L9 Module List (35 Modules)

## How to Use

1. Pick a module from the list below
2. Open `spec_generator.md`
3. Replace the module name/description
4. Paste into Perplexity Labs
5. Save the output YAML
6. Repeat for next module

---

## Tier 0: Core Infrastructure

| Module | Description |
|--------|-------------|
| `config_loader` | Environment and YAML configuration management with validation |
| `structlog_setup` | Centralized structlog configuration for all L9 modules |

## Tier 1: Database & Memory

| Module | Description |
|--------|-------------|
| `postgres_pool` | Async PostgreSQL connection pool with health checks |
| `redis_cache` | Redis client wrapper with connection pooling |
| `memory_substrate` | PostgreSQL-backed memory storage with vector search |

## Tier 2: Core Services

| Module | Description |
|--------|-------------|
| `packet_protocol` | PacketEnvelope creation, validation, and serialization |
| `substrate_service` | Memory substrate read/write operations |
| `world_model_service` | Entity relationship tracking and state management |

## Tier 3: AIOS Runtime

| Module | Description |
|--------|-------------|
| `aios_runtime` | LLM chat completion routing and response handling |
| `tool_registry` | Tool registration and lookup for agent tool calls |
| `agent_dispatcher` | Route requests to appropriate agent handlers |

## Tier 4: External Adapters

| Module | Description |
|--------|-------------|
| `slack_webhook_adapter` | Inbound Slack webhook handler with HMAC verification |
| `email_triage_adapter` | Gmail API integration for email processing |
| `telegram_adapter` | Telegram bot webhook handler |
| `discord_adapter` | Discord bot event handler |
| `github_webhook_adapter` | GitHub webhook handler for repo events |
| `stripe_webhook_adapter` | Stripe payment event handler |
| `twilio_sms_adapter` | Twilio SMS webhook handler |
| `calendly_webhook_adapter` | Calendly scheduling event handler |

## Tier 5: API Routes

| Module | Description |
|--------|-------------|
| `health_routes` | Health check endpoints for all services |
| `chat_routes` | Public chat API endpoints |
| `admin_routes` | Admin dashboard API endpoints |
| `memory_routes` | Memory query and management API |
| `agent_routes` | Agent orchestration API endpoints |

## Tier 6: Background Workers

| Module | Description |
|--------|-------------|
| `email_poller` | Scheduled Gmail inbox polling |
| `memory_janitor` | Scheduled memory cleanup and archival |
| `metric_aggregator` | Periodic metric collection and rollup |
| `webhook_retry_worker` | Retry failed outbound webhooks |

## Tier 7: Research & Agents

| Module | Description |
|--------|-------------|
| `planner_agent` | Research query decomposition and step planning |
| `researcher_agent` | Evidence gathering with Perplexity integration |
| `critic_agent` | Quality evaluation and approval gating |
| `insight_extractor` | Extract and store insights from research |
| `research_graph` | LangGraph DAG for multi-agent research orchestration |
| `research_api` | REST API for research endpoints |

---

## Quick Start: First 5 Modules

Start with these to test the workflow:

1. `config_loader` (Tier 0) - No dependencies
2. `structlog_setup` (Tier 0) - No dependencies  
3. `packet_protocol` (Tier 2) - Core protocol
4. `slack_webhook_adapter` (Tier 4) - First adapter
5. `health_routes` (Tier 5) - Simple API routes

---

## Tracking Progress

| Module | Spec Done | Code Done | Wired |
|--------|-----------|-----------|-------|
| config_loader | ⬜ | ⬜ | ⬜ |
| structlog_setup | ⬜ | ⬜ | ⬜ |
| ... | ... | ... | ... |

