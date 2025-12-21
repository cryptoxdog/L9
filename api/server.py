"""
L9 API Server
=============

FastAPI application for L9 Phase 2 Secure AI OS.

Provides:
- REST API endpoints for OS, agent, and memory operations
- WebSocket endpoint for real-time agent communication
- World model API (optional, v1.1.0+)

Version: 0.5.0 (Research Factory Integration)
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Header
from pydantic import BaseModel
from openai import OpenAI
from api.memory.router import router as memory_router
from api.auth import verify_api_key
import api.db as db
import api.os_routes as os_routes
import api.agent_routes as agent_routes

# Optional: World Model API (v1.1.0+)
try:
    from api.world_model_api import router as world_model_router
    _has_world_model = True
except ImportError:
    _has_world_model = False

# Optional: Slack Adapter (v2.0+)
try:
    from api.routes.slack import router as slack_router
    from api.slack_adapter import SlackRequestValidator
    from api.slack_client import SlackAPIClient
    import httpx
    _has_slack = True
except ImportError:
    _has_slack = False

# Optional: Quantum Research Factory (v2.1+)
try:
    from services.research.research_api import router as research_router
    from services.research.graph_runtime import init_runtime, shutdown_runtime
    _has_research = True
except ImportError:
    _has_research = False

# Optional: Agent Executor (v2.2+)
try:
    from core.agents.executor import AgentExecutorService
    from core.agents.schemas import AgentConfig, ToolBinding
    _has_agent_executor = True
except ImportError:
    _has_agent_executor = False

# Optional: AIOS Runtime (v2.2+)
try:
    from core.aios.runtime import AIOSRuntime, create_aios_runtime
    _has_aios_runtime = True
except ImportError:
    _has_aios_runtime = False

# Optional: Tool Registry Adapter (v2.2+)
try:
    from core.tools.registry_adapter import ExecutorToolRegistry, create_executor_tool_registry
    _has_tool_registry = True
except ImportError:
    _has_tool_registry = False

# Optional: Research Factory (v2.3+)
try:
    from api.routes.factory import router as factory_router
    _has_factory = True
except ImportError:
    _has_factory = False

# Optional: Governance Engine (v2.4+)
try:
    from core.governance.engine import GovernanceEngineService, create_governance_engine
    from core.governance.loader import PolicyLoadError, InvalidPolicyError
    _has_governance = True
except ImportError:
    _has_governance = False

# Optional: Kernel-Aware Agent Registry (v2.5+)
try:
    from core.agents.kernel_registry import create_kernel_aware_registry, KernelAwareAgentRegistry
    _has_kernel_registry = True
except ImportError:
    _has_kernel_registry = False

# Optional: Calendar Adapter (v2.6+)
try:
    from api.adapters.calendar_adapter.routes.calendar_adapter import router as calendar_adapter_router
    from api.adapters.calendar_adapter.config import get_config as get_calendar_config
    _has_calendar_adapter = True
except ImportError:
    _has_calendar_adapter = False

# Optional: Email Adapter (v2.6+)
try:
    from api.adapters.email_adapter.routes.email_adapter import router as email_adapter_router
    from api.adapters.email_adapter.config import get_config as get_email_config
    _has_email_adapter = True
except ImportError:
    _has_email_adapter = False

# Optional: Twilio Adapter (v2.6+)
try:
    from api.adapters.twilio_adapter.routes.twilio_adapter import router as twilio_adapter_router
    from api.adapters.twilio_adapter.config import get_config as get_twilio_config
    _has_twilio_adapter = True
except ImportError:
    _has_twilio_adapter = False

# Optional: Slack Webhook Adapter (v2.6+)
try:
    from api.adapters.slack_adapter.routes.slack_webhook import router as slack_webhook_adapter_router
    from api.adapters.slack_adapter.config import get_config as get_slack_webhook_config
    _has_slack_webhook_adapter = True
except ImportError:
    _has_slack_webhook_adapter = False

# Optional: Housekeeping Engine (v2.4+)
try:
    from memory.housekeeping import HousekeepingEngine, init_housekeeping_engine
    _has_housekeeping = True
except ImportError:
    _has_housekeeping = False

# Memory system imports
from memory.migration_runner import run_migrations
from memory.substrate_service import init_service, close_service, get_service

# Integration settings
from config.settings import settings

logger = logging.getLogger(__name__)

# Initialize DB
db.init_db()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager.
    Handles startup (migrations + memory init) and shutdown.
    """
    # ========================================================================
    # STARTUP: Validate required environment variables (fail-fast)
    # ========================================================================
    required_env_vars = ['OPENAI_API_KEY']  # MEMORY_DSN is optional, SLACK is optional
    recommended_env_vars = ['MEMORY_DSN', 'SLACK_BOT_TOKEN']
    
    missing_required = [v for v in required_env_vars if not os.getenv(v)]
    if missing_required:
        logger.critical(
            "FATAL: Missing required environment variables: %s. L9 cannot start.",
            missing_required,
        )
        raise RuntimeError(f"Missing required env vars: {missing_required}")
    
    missing_recommended = [v for v in recommended_env_vars if not os.getenv(v)]
    if missing_recommended:
        logger.warning(
            "Missing recommended env vars (some features disabled): %s",
            missing_recommended,
        )
    
    # ========================================================================
    # STARTUP: Run migrations and initialize memory service
    # ========================================================================
    logger.info("Starting L9 API server...")
    
    # Get database URL
    database_url = os.getenv("MEMORY_DSN") or os.getenv("DATABASE_URL")
    if not database_url:
        logger.warning(
            "MEMORY_DSN/DATABASE_URL not set. Memory system will not be available. "
            "Set MEMORY_DSN environment variable to enable memory."
        )
    else:
        try:
            # Run migrations
            logger.info("Running database migrations...")
            migration_result = await run_migrations(database_url)
            logger.info(
                f"Migrations complete: {migration_result['applied']} applied, "
                f"{migration_result['skipped']} skipped, {migration_result['errors']} errors"
            )
            if migration_result["errors"]:
                logger.error(f"Migration errors: {migration_result['error_details']}")
            
            # Initialize memory service
            logger.info("Initializing memory service...")
            substrate_service = await init_service(
                database_url=database_url,
                embedding_provider_type=os.getenv("EMBEDDING_PROVIDER", "stub"),
                embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-large"),
                openai_api_key=os.getenv("OPENAI_API_KEY"),
            )
            logger.info("Memory service initialized")
            
            # Store in app state for route dependencies
            app.state.substrate_service = substrate_service
        except Exception as e:
            logger.error(f"Failed to initialize memory system: {e}", exc_info=True)
            # Don't fail startup, but log error
            app.state.substrate_service = None
    
    # Initialize Quantum Research Factory (if enabled)
    if _has_research and database_url:
        try:
            logger.info("Initializing Quantum Research Factory...")
            await init_runtime(database_url)
            app.state.research_enabled = True
            logger.info("Quantum Research Factory initialized at /research")
        except Exception as e:
            logger.error(f"Failed to initialize Research Factory: {e}", exc_info=True)
            app.state.research_enabled = False
    elif _has_research:
        logger.warning("Research Factory not initialized: database_url required")
        app.state.research_enabled = False
    
    # Initialize Governance Engine (if enabled)
    if _has_governance:
        try:
            policy_dir = os.getenv("POLICY_MANIFEST_DIR", "config/policies")
            logger.info("Initializing Governance Engine from %s...", policy_dir)
            
            substrate = getattr(app.state, "substrate_service", None)
            governance_engine = create_governance_engine(
                policy_dir=policy_dir,
                substrate_service=substrate,
            )
            
            app.state.governance_engine = governance_engine
            logger.info(
                "Governance Engine initialized: %d policies loaded",
                governance_engine.policy_count,
            )
        except (PolicyLoadError, InvalidPolicyError) as e:
            # Governance failure is critical - log but allow startup for dev
            logger.critical("Governance Engine failed to initialize: %s", str(e))
            app.state.governance_engine = None
        except Exception as e:
            logger.error("Failed to initialize Governance Engine: %s", str(e), exc_info=True)
            app.state.governance_engine = None
    else:
        app.state.governance_engine = None
    
    # Initialize Housekeeping Engine (if enabled and substrate available)
    if _has_housekeeping and hasattr(app.state, "substrate_service") and app.state.substrate_service:
        try:
            logger.info("Initializing Housekeeping Engine...")
            housekeeping = init_housekeeping_engine(app.state.substrate_service._repository)
            app.state.housekeeping_engine = housekeeping
            logger.info("Housekeeping Engine initialized")
        except Exception as e:
            logger.error("Failed to initialize Housekeeping Engine: %s", str(e))
            app.state.housekeeping_engine = None
    else:
        app.state.housekeeping_engine = None
    
    # Initialize Agent Executor (if enabled and substrate available)
    if _has_agent_executor and hasattr(app.state, "substrate_service") and app.state.substrate_service:
        try:
            logger.info("Initializing Agent Executor...")
            
            # Use real AIOS runtime if available, otherwise stub
            if _has_aios_runtime:
                aios_runtime = create_aios_runtime()
                logger.info("Using real AIOSRuntime")
            else:
                class StubAIOSRuntime:
                    """Stub AIOS runtime - returns direct responses."""
                    async def execute_reasoning(self, context):
                        from core.agents.schemas import AIOSResult
                        return AIOSResult.response(
                            "AIOS runtime not yet implemented. Context received.",
                            tokens_used=0
                        )
                aios_runtime = StubAIOSRuntime()
                logger.info("Using stub AIOSRuntime")
            
            # Use real tool registry if available, otherwise stub
            if _has_tool_registry:
                # Connect governance engine if available
                gov_engine = getattr(app.state, "governance_engine", None)
                tool_registry = create_executor_tool_registry(
                    governance_enabled=True,
                    governance_engine=gov_engine,
                )
                logger.info(
                    "Using real ExecutorToolRegistry (governance=%s)",
                    "attached" if gov_engine else "legacy",
                )
            else:
                class StubToolRegistry:
                    """Stub tool registry - no tools available."""
                    async def dispatch_tool_call(self, tool_id, arguments, context):
                        from core.agents.schemas import ToolCallResult
                        from uuid import uuid4
                        return ToolCallResult(
                            call_id=uuid4(),
                            tool_id=tool_id,
                            success=False,
                            error="Tool registry not yet implemented"
                        )
                    
                    def get_approved_tools(self, agent_id, principal_id):
                        return []
                tool_registry = StubToolRegistry()
                logger.info("Using stub ToolRegistry")
            
            # Initialize agent registry with kernel loading
            if _has_kernel_registry:
                try:
                    logger.info("Initializing Kernel-Aware Agent Registry...")
                    agent_registry = create_kernel_aware_registry()
                    app.state.agent_registry = agent_registry
                    logger.info(
                        "Kernel-Aware Agent Registry initialized: kernel_state=%s",
                        agent_registry.get_kernel_state(),
                    )
                except RuntimeError as e:
                    # Kernel loading failed - this is critical
                    logger.critical("FATAL: %s", str(e))
                    # In production, you might want to crash here
                    # For dev, fall back to stub
                    logger.warning("Falling back to stub agent registry")
                    agent_registry = None
            else:
                agent_registry = None
            
            # Fallback stub registry if kernel registry unavailable
            if agent_registry is None:
                class StubAgentRegistry:
                    """Stub agent registry with default agent."""
                    def get_agent_config(self, agent_id):
                        return AgentConfig(
                            agent_id=agent_id,
                            personality_id=agent_id,
                            system_prompt="You are a helpful L9 AI assistant.",
                        )
                    
                    def agent_exists(self, agent_id):
                        return True
                agent_registry = StubAgentRegistry()
                logger.warning("Using stub agent registry (kernels not loaded)")
            
            # Create executor
            executor = AgentExecutorService(
                aios_runtime=aios_runtime,
                tool_registry=tool_registry,
                substrate_service=app.state.substrate_service,
                agent_registry=agent_registry,
            )
            
            app.state.agent_executor = executor
            app.state.aios_runtime = aios_runtime
            app.state.tool_registry = tool_registry
            logger.info("Agent Executor initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Agent Executor: {e}", exc_info=True)
            app.state.agent_executor = None
    elif _has_agent_executor:
        logger.warning("Agent Executor not initialized: substrate_service required")
        app.state.agent_executor = None
    
    # Initialize Slack adapter (if enabled)
    if _has_slack:
        try:
            slack_signing_secret = os.getenv("SLACK_SIGNING_SECRET")
            slack_bot_token = os.getenv("SLACK_BOT_TOKEN")
            
            if slack_signing_secret and slack_bot_token:
                logger.info("Initializing Slack adapter...")
                
                # Initialize Slack components
                validator = SlackRequestValidator(slack_signing_secret)
                http_client = httpx.AsyncClient()
                slack_client = SlackAPIClient(
                    bot_token=slack_bot_token,
                    http_client=http_client,
                )
                
                # Store in app state for route dependencies
                app.state.slack_validator = validator
                app.state.slack_client = slack_client
                app.state.aios_base_url = os.getenv("AIOS_BASE_URL", "http://localhost:8000")
                app.state.http_client = http_client
                
                logger.info("Slack adapter initialized")
            else:
                logger.warning(
                    "Slack adapter not initialized: SLACK_SIGNING_SECRET or SLACK_BOT_TOKEN not set"
                )
                app.state.slack_validator = None
                app.state.slack_client = None
        except Exception as e:
            logger.error(f"Failed to initialize Slack adapter: {e}", exc_info=True)
            app.state.slack_validator = None
            app.state.slack_client = None
    
    # ========================================================================
    # NEO4J GRAPH INTEGRATIONS (v2.7+)
    # ========================================================================
    
    # Validate Neo4j URI format (if set)
    neo4j_uri = os.getenv('NEO4J_URI')
    if neo4j_uri:
        valid_prefixes = ('bolt://', 'neo4j://', 'neo4j+s://', 'neo4j+ssc://')
        if not neo4j_uri.startswith(valid_prefixes):
            logger.error(
                f"Invalid NEO4J_URI format: {neo4j_uri}. "
                f"Must start with one of: {valid_prefixes}"
            )
            raise ValueError(f"Invalid NEO4J_URI format: {neo4j_uri}")
    
    # Initialize Neo4j client (optional, graceful if unavailable)
    try:
        from memory.graph_client import get_neo4j_client, close_neo4j_client
        neo4j = await get_neo4j_client()
        if neo4j and neo4j.is_available():
            app.state.neo4j_client = neo4j
            logger.info("Neo4j graph client initialized")
            
            # Register L9 tools in graph (for dependency tracking)
            try:
                from core.tools.tool_graph import register_l9_tools
                tool_count = await register_l9_tools()
                logger.info(f"Registered {tool_count} tools in Neo4j graph")
            except Exception as e:
                logger.warning(f"Failed to register tools in Neo4j: {e}")
        else:
            app.state.neo4j_client = None
            logger.info("Neo4j not available - graph features disabled")
    except ImportError:
        app.state.neo4j_client = None
        logger.debug("Neo4j client not available")
    except Exception as e:
        app.state.neo4j_client = None
        logger.warning(f"Failed to initialize Neo4j: {e}")
    
    # Initialize Redis client (optional, graceful if unavailable)
    try:
        from runtime.redis_client import get_redis_client, close_redis_client
        redis = await get_redis_client()
        if redis and redis.is_available():
            app.state.redis_client = redis
            logger.info("Redis client initialized")
        else:
            app.state.redis_client = None
            logger.info("Redis not available - using in-memory fallbacks")
    except ImportError:
        app.state.redis_client = None
        logger.debug("Redis client not available")
    except Exception as e:
        app.state.redis_client = None
        logger.warning(f"Failed to initialize Redis: {e}")
    
    # Store rate limiter in app state
    try:
        from runtime.rate_limiter import RateLimiter
        app.state.rate_limiter = RateLimiter()
        logger.info("Rate limiter initialized")
    except ImportError:
        app.state.rate_limiter = None
    
    # Initialize Permission Graph (RBAC via Neo4j)
    try:
        from core.security.permission_graph import PermissionGraph
        
        if hasattr(app.state, 'neo4j_client') and app.state.neo4j_client:
            app.state.permission_graph = PermissionGraph
            logger.info("✓ Permission Graph initialized (Neo4j-backed)")
        else:
            app.state.permission_graph = None
            logger.info("Permission Graph not available (requires Neo4j)")
    except ImportError:
        app.state.permission_graph = None
        logger.debug("Permission Graph module not available")
    except Exception as e:
        app.state.permission_graph = None
        logger.warning(f"Failed to initialize Permission Graph: {e}")
    
    # ========================================================================
    # STARTUP VALIDATION: Enforce required components are initialized
    # ========================================================================
    
    # Validate Neo4j (fail-fast if URI set but connection failed)
    if os.getenv('NEO4J_URI'):
        if not hasattr(app.state, 'neo4j_client') or not app.state.neo4j_client:
            logger.critical("NEO4J_URI set but connection failed - graph features disabled")
            # Note: Not fatal - Neo4j is optional for dev mode
        else:
            logger.info("✓ Neo4j validation passed")
    
    # Validate Permission Graph (required if Slack is enabled)
    if os.getenv('SLACK_BOT_TOKEN'):
        if not hasattr(app.state, 'permission_graph') or not app.state.permission_graph:
            logger.warning(
                "Slack enabled but Permission Graph not available. "
                "RBAC checks will be skipped."
            )
        else:
            logger.info("✓ Permission Graph validation passed (Slack protected)")
    
    # Validate kernel-aware agent registry (if enabled)
    if _has_kernel_registry:
        if not hasattr(app.state, 'agent_registry') or app.state.agent_registry is None:
            logger.critical("STARTUP VALIDATION FAILED: agent_registry not initialized")
            # In dev mode, we continue; in prod, this would be fatal
        elif hasattr(app.state.agent_registry, 'get_kernel_state'):
            kernel_state = app.state.agent_registry.get_kernel_state()
            if kernel_state != "ACTIVE":
                logger.critical(
                    "STARTUP VALIDATION FAILED: Kernels not ACTIVE (state=%s)",
                    kernel_state,
                )
            else:
                logger.info("✓✓✓ L9 FULLY INITIALIZED WITH ACTIVE KERNELS ✓✓✓")
    
    # Validate rate limiter
    if not hasattr(app.state, 'rate_limiter') or app.state.rate_limiter is None:
        logger.warning("STARTUP VALIDATION: Rate limiter not initialized")
    
    yield
    
    # ========================================================================
    # SHUTDOWN: Clean up memory service and Slack adapter
    # ========================================================================
    logger.info("Shutting down L9 API server...")
    
    # Cleanup Research Factory
    if _has_research and getattr(app.state, "research_enabled", False):
        try:
            await shutdown_runtime()
            logger.info("Research Factory shutdown")
        except Exception as e:
            logger.error(f"Error shutting down Research Factory: {e}")
    
    # Cleanup Slack HTTP client
    if _has_slack and hasattr(app.state, "http_client") and app.state.http_client:
        try:
            await app.state.http_client.aclose()
            logger.info("Slack HTTP client closed")
        except Exception as e:
            logger.error(f"Error closing Slack HTTP client: {e}")
    
    # Cleanup Neo4j client
    if hasattr(app.state, "neo4j_client") and app.state.neo4j_client:
        try:
            from memory.graph_client import close_neo4j_client
            await close_neo4j_client()
            logger.info("Neo4j client closed")
        except Exception as e:
            logger.error(f"Error closing Neo4j client: {e}")
    
    # Cleanup Redis client
    if hasattr(app.state, "redis_client") and app.state.redis_client:
        try:
            from runtime.redis_client import close_redis_client
            await close_redis_client()
            logger.info("Redis client closed")
        except Exception as e:
            logger.error(f"Error closing Redis client: {e}")
    
    # Cleanup memory service
    try:
        await close_service()
        logger.info("Memory service closed")
    except Exception as e:
        logger.error(f"Error closing memory service: {e}")


# FastAPI App
app = FastAPI(
    title="L9 Phase 2 Secure AI OS",
    lifespan=lifespan,
)


# =============================================================================
# Global Exception Handler with Neo4j Error Tracking
# =============================================================================
from fastapi import Request
from fastapi.responses import JSONResponse


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler that logs errors to Neo4j for causality tracking.
    """
    # Log to Neo4j (best-effort, non-blocking)
    try:
        from core.error_tracking import log_error_to_graph
        import asyncio
        asyncio.create_task(log_error_to_graph(
            error=exc,
            context={
                "endpoint": str(request.url.path),
                "method": request.method,
            },
            source=f"api:{request.url.path}",
        ))
    except ImportError:
        pass  # Error tracking not available
    except Exception:
        pass  # Don't fail request due to error tracking
    
    # Standard error response
    logger.error(f"Unhandled exception at {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

# Basic Root
@app.get("/")
def root():
    return {
        "status": "L9 Phase 2 AI OS", 
        "version": "0.5.0",
        "features": {
            "memory_substrate": True,
            "quantum_research": _has_research,
            "slack_adapter": _has_slack,
            "world_model": _has_world_model,
            "agent_executor": _has_agent_executor,
            "aios_runtime": _has_aios_runtime,
            "tool_registry": _has_tool_registry,
            "research_factory": _has_factory,
            "calendar_adapter": _has_calendar_adapter,
            "email_adapter": _has_email_adapter,
            "twilio_adapter": _has_twilio_adapter,
            "slack_webhook_adapter": _has_slack_webhook_adapter,
        }
    }


# Health Check (Docker healthcheck endpoint)
@app.get("/health")
async def health():
    """
    Root health check endpoint for Docker healthchecks and load balancers.
    Returns basic status without requiring authentication.
    """
    return {"status": "ok", "service": "l9-api"}


# Neo4j Health Check
@app.get("/health/neo4j")
async def neo4j_health():
    """
    Neo4j graph database health check.
    Returns healthy if connected, unavailable if not configured.
    """
    if not hasattr(app.state, 'neo4j_client') or not app.state.neo4j_client:
        return {"status": "unavailable", "message": "Neo4j not configured"}
    
    try:
        result = await app.state.neo4j_client.run_query("RETURN 1 as check")
        if result:
            return {"status": "healthy", "neo4j": True}
        return {"status": "unhealthy", "message": "Query returned no results"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# Chat endpoint (from server_memory.py for compatibility)
class ChatRequest(BaseModel):
    message: str
    system_prompt: str | None = None

class ChatResponse(BaseModel):
    reply: str

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    chat_client = OpenAI(api_key=OPENAI_API_KEY)
else:
    chat_client = None

@app.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    authorization: str = Header(None),
    _: bool = Depends(verify_api_key),
):
    """
    Basic LLM chat endpoint using OpenAI.
    Ingests both request and response to memory for audit trail.
    """
    if not chat_client:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
    
    from memory.ingestion import ingest_packet
    from memory.substrate_models import PacketEnvelopeIn
    
    try:
        messages = []
        if payload.system_prompt:
            messages.append({"role": "system", "content": payload.system_prompt})
        else:
            messages.append({
                "role": "system",
                "content": (
                    "You are L, an infrastructure-focused assistant connected to an L9 "
                    "backend and memory system. Be concise, precise, and avoid destructive "
                    "actions. When appropriate, suggest using tools like the CTO agent."
                ),
            })
        messages.append({"role": "user", "content": payload.message})

        completion = chat_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
        )
        reply = completion.choices[0].message.content
        
        # Ingest chat interaction to memory (audit trail)
        try:
            packet_in = PacketEnvelopeIn(
                packet_type="chat_interaction",
                payload={
                    "user_message": payload.message,
                    "system_prompt": payload.system_prompt,
                    "assistant_reply": reply,
                    "model": "gpt-4.1-mini",
                },
                metadata={"agent": "chat_api", "source": "server"},
            )
            await ingest_packet(packet_in)
        except Exception as mem_err:
            # Log but don't fail the request if memory ingestion fails
            logger.warning(f"Failed to ingest chat to memory: {mem_err}")
        
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat backend error: {e}")

# --- Routers ---
# OS health + metrics + routing
app.include_router(os_routes.router, prefix="/os")

# Background agent tasking
app.include_router(agent_routes.router, prefix="/agent")

# Persistent memory router
app.include_router(memory_router, prefix="/memory")

# World Model router (v1.1.0+)
if _has_world_model:
    app.include_router(world_model_router)

# Slack adapter router (v2.0+)
if _has_slack:
    app.include_router(slack_router)

# Quantum Research Factory router (v2.1+)
if _has_research:
    app.include_router(research_router)

# Research Factory router (v2.3+)
if _has_factory:
    app.include_router(factory_router)

# Calendar Adapter router (v2.6+)
if _has_calendar_adapter:
    app.include_router(calendar_adapter_router)

# Email Adapter router (v2.6+)
if _has_email_adapter:
    app.include_router(email_adapter_router)

# Twilio Adapter router (v2.6+)
if _has_twilio_adapter:
    app.include_router(twilio_adapter_router)

# Slack Webhook Adapter router (v2.6+)
if _has_slack_webhook_adapter:
    app.include_router(slack_webhook_adapter_router)

# === Legacy Webhook Routers (gated by toggle flags) ===
# These are the older webhook routers from server_memory.py for backward compatibility

# Slack Events API (legacy)
if settings.slack_app_enabled:
    try:
        from api.webhook_slack import router as webhook_slack_router
        app.include_router(webhook_slack_router)
    except Exception as e:
        logger.warning(f"Failed to load legacy Slack webhook router: {e}")

# Mac Agent API
if settings.mac_agent_enabled:
    try:
        from api.webhook_mac_agent import router as mac_agent_router
        app.include_router(mac_agent_router)
    except Exception as e:
        logger.warning(f"Failed to load Mac Agent router: {e}")

# Twilio webhook router (legacy)
if settings.twilio_enabled:
    try:
        from api.webhook_twilio import router as twilio_webhook_router
        app.include_router(twilio_webhook_router)
    except Exception as e:
        logger.warning(f"Failed to load legacy Twilio webhook router: {e}")

# WABA (WhatsApp Business Account - native Meta) (legacy)
if settings.waba_enabled:
    try:
        from api.webhook_waba import router as waba_router
        app.include_router(waba_router)
    except Exception as e:
        logger.warning(f"Failed to load WABA router: {e}")

# Email integration (legacy)
if settings.email_enabled:
    try:
        from api.webhook_email import router as email_webhook_router
        app.include_router(email_webhook_router)
    except ImportError:
        # webhook_email.py might not exist - that's okay
        pass
    except Exception as e:
        logger.warning(f"Failed to load legacy Email webhook router: {e}")
    
    # Email Agent API
    try:
        from email_agent.router import router as email_agent_router
        app.include_router(email_agent_router)
    except Exception as e:
        logger.warning(f"Failed to load Email Agent router: {e}")


# Startup + Shutdown events (if the modules expose them)
# NOTE: Migrations and memory init are handled in lifespan() above
@app.on_event("startup")
async def on_startup():
    if hasattr(agent_routes, "startup"):
        await agent_routes.startup()

@app.on_event("shutdown")
async def on_shutdown():
    if hasattr(agent_routes, "shutdown"):
        await agent_routes.shutdown()


# =============================================================================
# WebSocket Agent Endpoint
# =============================================================================

from core.schemas.event_stream import AgentHandshake

# Import the shared singleton orchestrator instance
from runtime.websocket_orchestrator import ws_orchestrator


@app.websocket("/ws/agent")
async def agent_ws_endpoint(websocket: WebSocket) -> None:
    """
    WebSocket entrypoint for L9 Mac Agents and other workers.
    
    Protocol:
    1) Client connects and sends AgentHandshake JSON.
    2) Server validates handshake and registers the agent_id.
    3) Subsequent frames are EventMessage JSON payloads.
    4) On disconnect, agent is automatically unregistered.
    
    Example client connection:
        import websockets
        import json
        
        async with websockets.connect("ws://localhost:8000/ws/agent") as ws:
            # Step 1: Send handshake
            await ws.send(json.dumps({
                "agent_id": "mac-agent-1",
                "agent_version": "1.0.0",
                "capabilities": ["shell", "memory_read"]
            }))
            
            # Step 2: Send/receive events
            await ws.send(json.dumps({
                "type": "heartbeat",
                "agent_id": "mac-agent-1",
                "payload": {"running_tasks": 0}
            }))
    """
    await websocket.accept()
    agent_id: str | None = None
    
    try:
        # Step 1: Wait for handshake
        raw = await websocket.receive_json()
        handshake = AgentHandshake.model_validate(raw)
        agent_id = handshake.agent_id
        
        # Register with orchestrator (store handshake metadata)
        await ws_orchestrator.register(
            agent_id,
            websocket,
            metadata={
                "agent_version": handshake.agent_version,
                "capabilities": handshake.capabilities,
                "hostname": handshake.hostname,
                "platform": handshake.platform,
            }
        )
        
        # Step 2: Message loop
        while True:
            data = await websocket.receive_json()
            
            # Ingest WebSocket event as packet (canonical memory entrypoint)
            try:
                from memory.ingestion import ingest_packet
                from memory.substrate_models import PacketEnvelopeIn
                
                packet_in = PacketEnvelopeIn(
                    packet_type="websocket_event",
                    payload=data,
                    metadata={"agent": agent_id, "source": "websocket"},
                )
                await ingest_packet(packet_in)
            except Exception as e:
                # Log but don't fail WebSocket handling if memory ingestion fails
                logger.warning(f"Failed to ingest WebSocket event: {e}")
            
            await ws_orchestrator.handle_incoming(agent_id, data)
            
    except WebSocketDisconnect:
        # Clean disconnect
        if agent_id:
            await ws_orchestrator.unregister(agent_id)
    except Exception as exc:
        # Unexpected error - log and cleanup
        import logging
        logging.getLogger(__name__).error(
            "WebSocket error for agent %s: %s",
            agent_id or "unknown",
            exc
        )
        if agent_id:
            await ws_orchestrator.unregister(agent_id)
