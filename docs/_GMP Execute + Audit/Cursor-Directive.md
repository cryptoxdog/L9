STEP 1 — CAPABILITY CONFIRMATION
CAPABILITIES_CONFIRMED:

Global search capabilities: 
Semantic search across the workspace, exact string/regex via grep, file pattern matching via glob

File operations: 
Read, write, modify, delete; preserve formatting and structure
Multi-file reasoning: Analyze relationships across files, infer architecture, detect patterns and inconsistencies

Architecture inference: Understand layered systems, module boundaries, dependency graphs, version evolution

Development strategy: Propose refactors, migrations, feature implementations aligned with project conventions

Code generation: 
Scaffolds, modules, tests, configs, pipelines following project patterns
Cross-version analysis: Compare V1.0/V2.0/V3.0/V3.5, identify migration paths, detect fragmentation

Governance awareness: Enforce .cursor/rules/, canonical YAML headers, file naming conventions, architectural contracts

Reasoning stack application: Apply architectural/engineering/research/CEO/operator reasoning stacks per L9-Agent-Specs.yaml

Learning system integration: Reference learned-lessons.md, prevent repeated mistakes, apply quick fixes

Deployment awareness: Understand Docker, Neo4j, Redis, VPS deployment patterns, migration plans

Agent role selection: Route to L9_Architect/L9_Engineer/L9_Researcher/L9_CEO/L9_Operator based on task intent

STEP 2 — GLOBAL PROJECT ANALYSIS
PROJECT_ANALYSIS:
Architecture:
Multi-version autonomous AI agent framework (L9 Reasoning Agent V1.0 → V3.5)
Strict separation: aeos/ (specs/docs), core/ (runtime reasoning), agents/ (behaviors)
9-phase architecture: OS Spawner → Operations → Governance → Board Swarm → COSE → Dashboard → Autonomy → Capital

Reasoning stacks: 
architectural, engineering, research, CEO, operator (defined in L9-Agent-Specs.yaml)
Knowledge graph: Neo4j for memory, Redis for state, Supabase integration
VPS deployment: Docker Compose with Traefik, FastAPI runtime, operational on Hetzner

Conventions:
Canonical YAML headers required (title, purpose, version, created, owner, tags, domain, type, production_ready)
File naming: kebab-case for prompts, CAPS for reports/briefs, <project>_<module>_<component>_v<version>.<ext>
No READMEs in subfolders unless 50+ files
Output inline by default; only create files for explicit deliverables
Header preservation: never replace, only add fields and update timestamps

Naming patterns:
Agents: L9_Architect, L9_Engineer, L9_Researcher, L9_CEO, L9_Operator
Modules: core/reasoning/, core/agents/, core/governance/, modules/tot/, modules/ril/
Specs: aeos/governance/, aeos/reasoning/, aeos/board/
Component IDs: [LAYER-DOMAIN-###] (e.g., CORE-FILE-001)

Existing agents/modules:
Core agents: ceo_agent.py, research_agent.py, chimera_agent.py
Reasoning: ToTh, RAFA, RIL, PSI-KT, Agent Q, MuZero
Governance: FORGE Board, Meta Oversight, EEIS, Progressive Autonomy
Learning: PSI-KT, RPKT, R-Loop Trainer

Capital: ACE (Capital Flow Engine)
Missing pieces:
Migration from aeos/ Python files to core/ runtime (per migration plan)
Neo4j schema deployment (7 Cypher files pending)
Feature flags for incremental enablement
Power Commands API endpoints
COSE synergy engine runtime implementation
Execution router migration

Project purpose:
Autonomous AI development framework for creating/managing intelligent automation
Self-improving system that learns from mistakes, maintains integrity, deploys agents
Domain-agnostic with n8n workflow specialization
Recursive self-healing with governance, security validation, pattern detection

Engineering direction:
V3.5 deployed and operational; migration from aeos/ to runtime in progress
Incremental enablement with feature flags
Dependency-aware execution order (ToT → RIL → PSI-KT → etc.)
Production-ready with Neo4j/Redis integration

Errors/fragmentation:
Version overlap: V1.0, V2.0, V3.0, V3.5 with similar structures
Conceptual vs runtime: aeos/ contains Python files that should be in core/
Migration incomplete: 8 Python files + 7 Neo4j schemas pending migration
Governance rules duplicated across versions (should consolidate)
Areas needing refactor:
Consolidate .cursor/rules/ across versions
Complete aeos/ → core/ migration
Standardize component IDs and metadata
Unify deployment patterns across versions

STEP 3 — TASK/OBJECTIVE ANALYSIS
OBJECTIVE_INFERENCE:
Goal: Generate a prompt template that ensures Cursor:
Respects architectural boundaries (aeos/ vs core/ vs agents/)
Applies correct reasoning stacks based on task type
Follows file naming and header conventions
Selects appropriate L9 agent roles (Architect/Engineer/Researcher/CEO/Operator)
Prevents architectural violations (e.g., runtime code in aeos/)
Uses fact-first approach (read files fully, no assumptions)
Applies learning system patterns (prevents repeated mistakes)
Maintains version awareness (V3.5 is current production)
Enforces governance rules from .cursor/rules/
Produces structured outputs with proper YAML headers

Naming Conventions:
Prompts: kebab-case (e.g., automation-builder-agent.md)
Reports/Briefs: CAPS (e.g., N8N_PHASE1_DELIVERY_LOG.md)
Components: <project>_<module>_<component>_v<version>.<ext>
Component IDs: [LAYER-DOMAIN-###] (e.g., CORE-FILE-001)
File Creation Policy:
Output inline in chat by default
Only create files for explicit deliverables (code, configs, frameworks)
NO auto-generated briefs/summaries/reports (chat history = record)
NO READMEs in subfolders unless folder has 50+ files
Header Preservation:
NEVER replace existing headers when updating files
ONLY ADD new fields and UPDATE updated timestamp
PRESERVE all original created dates and metadata


BEHAVIORAL RULES
FACT-FIRST APPROACH:
NEVER make assumptions
ALWAYS read files start-to-finish (don't assume from headers/metadata)
Obtain facts first, then determine course of action
Evidence-based decision making is mandatory

PRE-ACTION COMPLIANCE CHECK:
Before creating ANY file, verify:
Is this an explicit deliverable request?
Is this a README in subfolder with <50 files?
Is this an auto-generated brief/summary/report?
If ANY violation → output inline in chat instead

Learning System Integration:
Reference GlobalCommands/learned-lessons.md before making decisions
Prevent repeated mistakes from learning database
Apply quick fixes from learning/quick-fixes.md
Check learning/repeated-mistakes.md for zero-tolerance errors

Version Awareness:
V3.5 is current production version
Migration from aeos/ to core/ in progress (follow migration plan)
Neo4j schemas pending deployment (7 Cypher files)
Feature flags enable incremental enablement

OUTPUT REQUIREMENTS
Structured Outputs:
Always include reasoning trace
Provide confidence metrics
Include validation pass/fail
Show architectural tradeoff review (for architectural tasks)
Include failure mode review (for engineering tasks)

Code References:
Use startLine:endLine:filepath format for existing code
Use standard markdown code blocks for new/proposed code
NEVER mix formats

GOVERNANCE ENFORCEMENT
Invariants (NEVER VIOLATE):
no_autonomous_goal_creation
no_scope_expansion_without_explicit_user_instruction
enforced_reasoning_stack: true
outputs_structured_only: true
agents_must_respect_permissions: true
commands_must_respect_permissions: true
agent_selection_matches_intent: true

When Unclear:
Check L9-Agent-Specs.yaml for agent permissions
Check docs/templates/L9_REPO_STRUCTURE_RULES.md for folder placement
Check .cursor/rules/ for governance rules
ASK before assuming

DEPLOYMENT AWARENESS
Current Status:
V3.5 deployed and operational on Hetzner VPS
Docker Compose with Traefik, Neo4j, Redis
FastAPI runtime with /api/tot/expand, /api/reason, /api/knowledge/query
Migration plan exists for aeos/ components

Migration Rules:
Follow dependency order: ToT → RIL → PSI-KT → Scenario Cache → Block Registry
Deploy Neo4j schemas first (foundation)
Enable components incrementally with feature flags
Never mutate Docker unless explicitly asked

ACTIVATION: When you receive a task, immediately:
Identify task type (architectural/engineering/research/CEO/operator)
Select appropriate reasoning stack
Select appropriate L9 agent role
Verify folder placement (aeos vs core vs agents)
Check learning system for known mistakes
Apply fact-first approach (read files fully)
Generate structured output with proper headers
Enforce all invariants and governance rules

CONFIRMATION: Before proceeding, confirm you understand:
Architectural boundaries (aeos/ vs core/ vs agents/)
Reasoning stack selection
Agent role permissions
File standards and naming conventions
Governance invariants
