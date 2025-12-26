# GMP-L.0 — Bootstrap & Initialization v1.1
## Lock Scope, Register L, Wire Tools, Load Identity (CANONICAL FORMAT)

You are C (Cursor) operating in the L9 repository.
You operate by fixed phases only. You do not redesign. You do not guess.
You report only via this prompt in PHASE 0–6 discipline.

============================================================================
PHASE 0 — RESEARCH & ANALYSIS
============================================================================

PURPOSE: Create complete, observable TODO list before edits begin.

ACTIONS:
1. Inspect: core/agents/registry.py (agent registration logic)
2. Inspect: core/tools/capabilities.py (tool enum + profiles) [file:152]
3. Inspect: core/tools/tool_graph.py (tool definitions, registration) [file:163]
4. Inspect: executor.py (agent instantiation path) [file:136]
5. Inspect: startup entry point (main.py or boot.py)

FINDINGS:
- AgentRegistry exists but has no "L" registered [registry.py line TBD]
- ToolName enum exists but lacks GMP_RUN, GIT_COMMIT, etc. [capabilities.py:152 line TBD]
- ToolGraph.register_tool() exists but is never called at startup [tool_graph.py:163 line TBD]
- AgentExecutorService._instantiate_agent() expects agent in registry [executor.py:136 line TBD]

### TODO PLAN

- [0.1] Create `core/agents/l_bootstrap.py` with `create_l_config()` + `bootstrap_l_agent()`
- [0.2] Extend `ToolName` enum in `capabilities.py:152` to add: GMP_RUN, GIT_COMMIT, MAC_AGENT_EXEC_TASK, MCP_CALL_TOOL
- [0.3] Create `L_CAPABILITIES` profile in `capabilities.py:152` defining tool scope/approval requirements
- [0.4] Define `L_TOOLS_DEFINITIONS` list in `tool_graph.py:163` with ToolDefinition objects
- [0.5] Extend `ToolDefinition` dataclass in `tool_graph.py:163` with: category, scope, risk_level, requires_igor_approval
- [0.6] Implement `ToolGraph.register_tool()` logic in `tool_graph.py:163` to write to Neo4j
- [0.7] Add bootstrap hook to startup entry point (identify & modify main.py/boot.py)
- [0.8] Initialize L's memory chunks via `initialize_l_memory()` in `l_bootstrap.py`

✅ PHASE 0 DEFINITION OF DONE:
• All TODOs use file paths and exact references
• No "maybe" or inferred work
• Execution plan frozen
• TODO IDs mapped [0.1]–[0.8]

============================================================================
PHASE 1 — BASELINE CONFIRMATION
============================================================================

PURPOSE: Prevent invisible failures. Confirm each location exists.

ACTIONS:
- [1.1] Confirm `capabilities.py:152` contains `class ToolName(str, Enum)` ✓
- [1.2] Confirm `tool_graph.py:163` contains `class ToolDefinition` ✓
- [1.3] Confirm `executor.py:136` contains `_instantiate_agent()` method ✓
- [1.4] Confirm agent registry exists and has `register_agent()` method ✓
- [1.5] Identify startup entry point (main.py, boot.py, app.py, __main__.py) — NOT YET CONFIRMED
- [1.6] Confirm substrate_service is available for memory writes ✓

✅ PHASE 1 DEFINITION OF DONE:
• All locations confirmed or blocked
• If startup entry point not found: STOP HERE

============================================================================
PHASE 2 — IMPLEMENTATION
============================================================================

PURPOSE: Apply all changes listed in TODOs. Maintain strict scope discipline.

### [0.1] Create l_bootstrap.py

FILE: `core/agents/l_bootstrap.py` (NEW)

```python
from core.agents.schemas import AgentConfig, ToolBinding
from core.tools.capabilities import L_CAPABILITIES
from core.tools.tool_graph import L_TOOLS_DEFINITIONS
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def create_l_config() -> AgentConfig:
    """Create L's agent configuration."""
    tool_bindings = [
        ToolBinding(
            tool_id=tool_def.name,
            description=tool_def.description,
            enabled=True,
            input_schema={"type": "object", "properties": {}},
        )
        for tool_def in L_TOOLS_DEFINITIONS
    ]
    
    return AgentConfig(
        agent_id="L",
        name="L (CTO)",
        description="Chief Technology Officer for Igor; architect and governor of L9",
        system_prompt=None,
        tools=tool_bindings,
        max_iterations=20,
        metadata={
            "role": "CTO",
            "authority": "Igor-only",
            "capabilities_profile": "L_CAPABILITIES",
        }
    )

async def bootstrap_l_agent(agent_registry, tool_registry) -> None:
    """Bootstrap L into the system."""
    l_config = await create_l_config()
    agent_registry.register_agent("L", l_config)
    
    for tool_def in L_TOOLS_DEFINITIONS:
        tool_registry.register_tool(tool_def)
    
    for tool_def in L_TOOLS_DEFINITIONS:
        await ToolGraph.register_tool(tool_def)
    
    logger.info("Bootstrap: L agent registered with %d tools", len(L_TOOLS_DEFINITIONS))

async def initialize_l_memory(substrate_service) -> None:
    """Initialize L's foundational memory chunks."""
    memory_chunks = [
        {
            "chunk_id": "meta_prompt_governance",
            "type": "governance_meta_prompts",
            "content": "One objective per invocation; stop on missing/conflicting inputs.",
        },
        {
            "chunk_id": "meta_prompt_reasoning",
            "type": "governance_meta_prompts",
            "content": "Separate facts from assumptions; label inference; Unknown over guessing.",
        },
        {
            "chunk_id": "authority_chain",
            "type": "authority_and_phase_map",
            "content": "Authority: Igor (CEO) → L (CTO) → L9 (runtime).",
        },
        {
            "chunk_id": "tool_approval_rules",
            "type": "governance_meta_prompts",
            "content": "GMP runs and git commits require Igor's explicit approval.",
        },
    ]
    
    for chunk in memory_chunks:
        await substrate_service.write_packet(
            PacketEnvelopeIn(
                packet_type="memory_chunk",
                payload=chunk,
                agent_id="L",
            )
        )
    
    logger.info("Bootstrap: L memory chunks initialized")
```

### [0.2] Extend ToolName enum

FILE: `capabilities.py:152`
LOCATION: After existing `ToolName` members
LINES: [INSERT AFTER FINAL EXISTING MEMBER]

```python
    # [0.2] Add new enum members:
    GMP_RUN = "gmp_run"
    GIT_COMMIT = "git_commit"
    MCP_CALL_TOOL = "mcp_call_tool"
    MAC_AGENT_EXEC_TASK = "mac_agent_exec_task"
```

### [0.3] Add L_CAPABILITIES profile

FILE: `capabilities.py:152`
LOCATION: After ToolName class definition
LINES: [APPEND NEW CONSTANT]

```python
# [0.3] Add capability profile for L
L_CAPABILITIES = AgentCapabilities(
    agent_id="L",
    capabilities=[
        Capability(tool=ToolName.MEMORY_READ, allowed=True),
        Capability(tool=ToolName.MEMORY_WRITE, allowed=True),
        Capability(tool=ToolName.GMP_RUN, allowed=True, scope="requires_igor_approval"),
        Capability(tool=ToolName.GIT_COMMIT, allowed=True, scope="requires_igor_approval"),
        Capability(tool=ToolName.MAC_AGENT_EXEC_TASK, allowed=True, scope="requires_igor_approval"),
        Capability(tool=ToolName.MCP_CALL_TOOL, allowed=True, scope="external"),
    ],
    default_allowed=False,
)
```

### [0.4] Define L_TOOLS_DEFINITIONS

FILE: `tool_graph.py:163`
LOCATION: After ToolDefinition class, before any existing tool lists
LINES: [NEW SECTION]

```python
# [0.4] Define L's tool palette
L_TOOLS_DEFINITIONS = [
    ToolDefinition(
        name="memory_search",
        description="Search L's memory for facts, decisions, and context",
        category="memory",
        scope="internal",
        risk_level="low",
        is_destructive=False,
        requires_igor_approval=False,
        agent_id="L",
    ),
    ToolDefinition(
        name="memory_write",
        description="Write findings and decisions to L's memory",
        category="memory",
        scope="internal",
        risk_level="medium",
        is_destructive=True,
        requires_igor_approval=False,
        agent_id="L",
    ),
    ToolDefinition(
        name="gmp_run",
        description="Propose a God Mode Prompt (GMP) run in Cursor (requires Igor approval)",
        category="execution",
        scope="internal",
        risk_level="high",
        is_destructive=True,
        requires_igor_approval=True,
        external_apis=["Cursor"],
        agent_id="L",
    ),
    ToolDefinition(
        name="git_commit",
        description="Propose a git commit to the repository (requires Igor approval)",
        category="execution",
        scope="internal",
        risk_level="high",
        is_destructive=True,
        requires_igor_approval=True,
        external_apis=["git"],
        agent_id="L",
    ),
    ToolDefinition(
        name="mac_agent_exec_task",
        description="Execute a Mac Agent task (shell, browser, etc.; requires Igor approval)",
        category="execution",
        scope="internal",
        risk_level="high",
        is_destructive=True,
        requires_igor_approval=True,
        agent_id="L",
    ),
    ToolDefinition(
        name="mcp_call_tool",
        description="Call an MCP tool (GitHub, Notion, Vercel, GoDaddy)",
        category="integration",
        scope="external",
        risk_level="medium",
        is_destructive=False,
        requires_igor_approval=False,
        agent_id="L",
    ),
]
```

### [0.5] Extend ToolDefinition

FILE: `tool_graph.py:163`
LOCATION: Inside ToolDefinition dataclass definition
LINES: [ADD AFTER EXISTING FIELDS]

```python
    # [0.5] New governance fields:
    category: str = "general"
    scope: str = "internal"
    risk_level: str = "low"
    is_destructive: bool = False
    requires_igor_approval: bool = False
    external_apis: list[str] = field(default_factory=list)
    agent_id: str | None = None
```

### [0.6] Implement ToolGraph.register_tool()

FILE: `tool_graph.py:163`
LOCATION: Inside ToolGraph class, new method
LINES: [NEW METHOD]

```python
    # [0.6] Implement registration logic
    @staticmethod
    async def register_tool(tool: ToolDefinition) -> bool:
        """Register a tool and its metadata into Neo4j."""
        neo4j = await ToolGraph._get_neo4j()
        if not neo4j:
            return False
        
        try:
            await neo4j.create_entity(
                entity_type="Tool",
                entity_id=tool.name,
                properties={
                    "name": tool.name,
                    "description": tool.description,
                    "category": tool.category,
                    "scope": tool.scope,
                    "risk_level": tool.risk_level,
                    "requires_igor_approval": tool.requires_igor_approval,
                    "is_destructive": tool.is_destructive,
                    "registered_at": datetime.utcnow().isoformat(),
                },
            )
            
            if tool.agent_id:
                await neo4j.create_relationship(
                    from_type="Agent",
                    from_id=tool.agent_id,
                    to_type="Tool",
                    to_id=tool.name,
                    rel_type="HAS_TOOL",
                    properties={
                        "scope": tool.scope,
                        "requires_approval": tool.requires_igor_approval,
                    }
                )
            
            return True
        except Exception as e:
            logger.warning(f"Failed to register tool {tool.name}: {e}")
            return False
```

### [0.7] Add bootstrap hook to startup

FILE: [IDENTIFIED IN PHASE 1.5]
LOCATION: Early in main() or app startup sequence
LINES: [TBD AFTER PHASE 1]

```python
    # [0.7] Bootstrap L before executor starts
    from core.agents.l_bootstrap import bootstrap_l_agent
    await bootstrap_l_agent(agent_registry, tool_registry)
```

### [0.8] Initialize L's memory chunks

FILE: `core/agents/l_bootstrap.py`
LOCATION: New function `initialize_l_memory()`
LINES: [PART OF 0.1]

(Implemented in Phase 2 [0.1])

✅ PHASE 2 DEFINITION OF DONE:
• Every TODO item [0.1]–[0.8] implemented
• No non-TODO edits occurred
• Line ranges documented for each change
• Code compiles without error

============================================================================
PHASE 3 — ENFORCEMENT
============================================================================

PURPOSE: Ensure all behavior is enforced via logic or test.

ACTIONS:

- [3.1] Add guard in `executor.py:136._instantiate_agent()` to verify tool registry has approved tools
  - ENFORCEMENT: If tool registry is empty for agent "L", raise ValueError
  - LOCATION: After line where `config.tools = approved_tools`

- [3.2] Add guard in bootstrap to verify L config was registered
  - ENFORCEMENT: After `agent_registry.register_agent("L", l_config)`, assert exists
  - LOCATION: In `bootstrap_l_agent()`

- [3.3] Add test: verify all L_TOOLS_DEFINITIONS are registered in Neo4j
  - TEST: `test_l_tools_registered()` in test suite
  - LOCATION: `tests/test_l_bootstrap.py` (NEW)

✅ PHASE 3 DEFINITION OF DONE:
• Enforcement logic exists for each critical TODO
• Deletion of enforcement code causes failure
• Tests pass
• Output: test results logged

============================================================================
PHASE 4 — VALIDATION
============================================================================

PURPOSE: Confirm work behaves as intended. Trigger real-world simulation.

ACTIONS:

- [4.1] Instantiate L agent via executor and verify all tools bound
  - TEST: Call `executor._instantiate_agent(task)` where agent_id="L"
  - EXPECTED: AgentInstance has 6+ tools bound

- [4.2] Verify high-risk tools are marked `requires_igor_approval=True`
  - TEST: Query Neo4j for "GMP_RUN" tool, check requires_igor_approval field
  - EXPECTED: True for GMP_RUN, GIT_COMMIT, MAC_AGENT_EXEC_TASK

- [4.3] Verify L's identity synced to memory
  - TEST: Query memory substrate for "identity" segment with agent_id="L"
  - EXPECTED: Returns 1+ chunk

✅ PHASE 4 DEFINITION OF DONE:
• All simulations pass
• Tool removal breaks expected behavior
• Incomplete setup fails

============================================================================
PHASE 5 — RECURSIVE SELF-VALIDATION
============================================================================

PURPOSE: Confirm all phases were completed exactly as instructed.

RECURSIVE CHECKS:

- ✓ Every TODO [0.1]–[0.8] appears across phases 0, 1, 2, 3, 4
- ✓ No change exists outside [0.1]–[0.8]
- ✓ No TODO was skipped
- ✓ No phase was collapsed
- ✓ Phase 0 (plan), Phase 1 (confirm), Phase 2 (implement), Phase 3 (enforce), Phase 4 (validate) all complete
- ✓ No assumptions detected (all references are concrete: file paths, line numbers, identifiers)
- ✓ Scope lock: bootstrap only, no design changes
- ✓ No "helpful" additions (logging, refactoring, style changes)

✅ PHASE 5 DEFINITION OF DONE:
• Recursive audit confirms scope compliance
• Zero drift confirmed
• Ready for Phase 6

============================================================================
PHASE 6 — FINAL AUDIT & REPORT GENERATION
============================================================================

PURPOSE: Lock system state and emit execution contract record.

ACTIONS:

1. Re-scan all changed files
2. Confirm line ranges match TODOs
3. Confirm no rogue edits
4. Write report to: `exec_report_gmp_l0_bootstrap.md` (REPO ROOT, NOT /opt/l9)

REPORT STRUCTURE (REQUIRED):

# EXECUTION REPORT — GMP-L.0 Bootstrap

## TODO PLAN
- [0.1] Create `core/agents/l_bootstrap.py` with `create_l_config()` + `bootstrap_l_agent()`
- [0.2] Extend `ToolName` enum in `capabilities.py:152`
- [0.3] Create `L_CAPABILITIES` profile in `capabilities.py:152`
- [0.4] Define `L_TOOLS_DEFINITIONS` list in `tool_graph.py:163`
- [0.5] Extend `ToolDefinition` dataclass in `tool_graph.py:163`
- [0.6] Implement `ToolGraph.register_tool()` logic in `tool_graph.py:163`
- [0.7] Add bootstrap hook to startup entry point
- [0.8] Initialize L's memory chunks via `initialize_l_memory()`

## PHASE CHECKLIST STATUS (0–6)
- [✓] Phase 0: TODO plan complete
- [✓] Phase 1: Baseline confirmed
- [✓] Phase 2: Implementation complete
- [✓] Phase 3: Enforcement wired
- [✓] Phase 4: Validation passed
- [✓] Phase 5: Recursive verification passed
- [✓] Phase 6: Report generated

## FILES MODIFIED + LINE RANGES
- `capabilities.py:152` — Lines [X]–[Y] (ToolName enum extension)
- `capabilities.py:152` — Lines [A]–[B] (L_CAPABILITIES profile)
- `tool_graph.py:163` — Lines [P]–[Q] (ToolDefinition extension)
- `tool_graph.py:163` — Lines [R]–[S] (L_TOOLS_DEFINITIONS)
- `tool_graph.py:163` — Lines [T]–[U] (register_tool implementation)
- `core/agents/l_bootstrap.py` — NEW FILE (create_l_config, bootstrap_l_agent, initialize_l_memory)
- `[STARTUP ENTRY]` — Lines [V]–[W] (bootstrap hook)

## TODO → CHANGE MAP
- [0.1] → `core/agents/l_bootstrap.py` (NEW)
- [0.2] → `capabilities.py:152` lines [X]–[Y]
- [0.3] → `capabilities.py:152` lines [A]–[B]
- [0.4] → `tool_graph.py:163` lines [R]–[S]
- [0.5] → `tool_graph.py:163` lines [P]–[Q]
- [0.6] → `tool_graph.py:163` lines [T]–[U]
- [0.7] → `[STARTUP ENTRY]` lines [V]–[W]
- [0.8] → `core/agents/l_bootstrap.py` (function part of 0.1)

## ENFORCEMENT + VALIDATION RESULTS
- [3.1] Guard in executor._instantiate_agent() — PASSED
- [3.2] Guard in bootstrap_l_agent() — PASSED
- [3.3] test_l_tools_registered() — PASSED
- [4.1] Agent instantiation with 6+ tools — PASSED
- [4.2] High-risk tools marked for approval — PASSED
- [4.3] Identity synced to memory — PASSED

## PHASE 5 RECURSIVE VERIFICATION
✓ All TODOs traced to code changes
✓ No extra files/functions created
✓ No formatting drift
✓ Scope locked: bootstrap only
✓ No assumptions in implementation
✓ Phase discipline maintained

## FINAL DECLARATION

> All phases (0–6) complete. No assumptions. No drift. Scope locked.
>
> **Bootstrap complete:** L is registered in agent registry with 6+ tools, all tools registered in Neo4j with governance metadata, L's identity and memory chunks initialized.
>
> Execution terminated. Output verified. Report stored at `exec_report_gmp_l0_bootstrap.md`.
>
> No further changes are permitted to this GMP. GMP-L.1 may now execute.

✅ PHASE 6 DEFINITION OF DONE:
• Report exists at required path
• All sections complete with real data
• Final declaration present verbatim
• No placeholders

============================================================================
FINAL DEFINITION OF DONE (GMP-L.0)

✓ PHASE 0–6 completed and documented
✓ All TODOs [0.1]–[0.8] implemented, enforced, validated, mapped
✓ L registered in agent registry with full config
✓ All L tools defined and registered in Neo4j
✓ L's identity and memory initialized
✓ No files modified outside TODO scope
✓ No phase skipped or collapsed
✓ Report written to required path
✓ Recursive verification (PHASE 5) passed
✓ Final declaration present

============================================================================
