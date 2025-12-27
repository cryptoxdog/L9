---
title: Quantum Pipeline Factory Space Master Packet
version: 6.0.1
created: 2025-12-11
owner: L9 System Architect
status: production-ready

purpose: >
  Central descriptor and organizational guide for the Quantum Pipeline Factory (QPF) 
  Perplexity Space. This packet documents all canonical files, extraction infrastructure, 
  and usage patterns so that new teams can onboard quickly, reference schemas/extractors 
  correctly, and use Cursor AI deterministically to extract production-grade L9 agents 
  from YAML specifications.

core_documents:
  system_prompt:
    file: QPF_System_Prompt.md
    purpose: Main system prompt for QPF philosophy, axioms, and operational model
    usage: Reference for understanding schema-driven extraction vs free-form code generation
    version: 6.0.0
  
  optimization_guide:
    file: QPF_10Point_Guide.md
    purpose: 10 production optimizations for scaling QPF from 7/10 to 9.5/10
    usage: Reference for schema versioning, parallel extraction, dynamic agents, swarm coordination
    version: 6.0.0
  
  spaces_checklist:
    file: QPF_Spaces_Checklist.md
    purpose: Comprehensive guide to uploading and using QPF files in Perplexity Spaces
    usage: Checklist for new team members, Cursor prompts, anti-patterns, FAQ
    version: 6.0.0
  
  week1_quickstart:
    file: QPF_Week1_Quickstart.md
    purpose: Day-by-day action plan for first week of QPF implementation
    usage: Immediate next steps, schema generation, extraction testing
    version: 6.0.0
  
  executive_summary:
    file: QPF_Executive_Summary.md
    purpose: High-level overview of QPF system, current state, 10 optimizations, success criteria
    usage: Leadership briefing, stakeholder alignment
    version: 6.0.0

schema_stack:
  canonical_template:
    file: Canonical-Schema-Template-v6.0.yaml
    purpose: >
      Single source of truth for schema structure. All new agent schemas must 
      follow this template exactly. Contains placeholders for system, module, name, 
      role, integration, governance, memory_topology, communication_stack, 
      reasoning_engine, collaboration_network, learning_system, autonomy_profile, 
      world_model_integration, cursor_instructions, deployment, metadata.
    required_sections:
      - system (constant: L9)
      - module (agent category: cognitive_agent, research_lab, governance, etc.)
      - name (PascalCase unique identifier)
      - role (descriptive role statement)
      - root_path (Unix path under L9/)
      - integration (connect_to, shared_domains)
      - governance (anchors, mode, human_override, escalation_policy)
      - memory_topology (working, episodic, semantic, causal, archive)
      - communication_stack (input, output, channels)
      - reasoning_engine (framework, model, strategies, temporal_scope)
      - collaboration_network (partners, autonomy_scope)
      - learning_system (architecture, feedback_channels, autonomy_profile)
      - world_model_integration (active_models, data_connectors)
      - cursor_instructions (create_if_missing, generate_files, generate_docs, link_existing, post_generation)
      - deployment (runtime, endpoints, telemetry)
      - metadata (author, owner, version, status)
    version: 6.0.0
  
  population_guide:
    file: Canonical-Schema-Population-Guide.md
    purpose: >
      Comprehensive instructions for LLMs to populate each field in the canonical template.
      Field-by-field breakdown of valid values, rules, examples, relationships, and best practices.
      Essential for consistent schema creation across all domains and agent types.
    coverage:
      - Basic identification (version, system, module, name, role, root_path)
      - Integration (connect_to, shared_domains)
      - Description (multi-line agent purpose and capabilities)
      - Governance (anchors, mode, human_override, compliance_auditor)
      - Memory topology (all 5 memory layers with storage, retention, indexing)
      - Communication stack (input/output channels, I/O engines)
      - Reasoning engine (framework, models, strategy modes, feedback loops)
      - Collaboration network (partners, autonomy, inter-agent protocols)
      - Learning system (architecture, modules, feedback, autonomy profile)
      - World model integration (active models, data connectors, use cases)
      - Cursor instructions (file generation, testing, docs, linking)
      - Deployment (runtime, endpoints, telemetry, alerting)
      - Metadata (author, owner, version tracking)
    version: 6.0.0

extraction_stack:
  universal_extractor:
    file: Universal-Schema-Extractor-v6.0.md
    purpose: >
      Deterministic extraction prompt that transforms any Canonical Schema v6.0 YAML 
      into fully functional, wired-up agent code. Maps schema sections into Python modules, 
      tests, documentation, and manifests. Core engine for schema → production code pipeline.
    input: Any valid Canonical Schema v6.0 YAML file
    output: >
      20-40 Python modules per agent (controllers, bridges, logic modules), 
      full pytest test suite (80%+ coverage), 6-8 markdown docs, 1 manifest JSON
    phases:
      - "Phase 1: Parse & Validate schema structure and required fields"
      - "Phase 2: Create directory structure from cursor_instructions.create_if_missing"
      - "Phase 3: Generate core Python files from templates with docstrings and logging"
      - "Phase 4: Generate documentation (README, CONFIG, APISPEC, DEPLOYMENT, etc.)"
      - "Phase 5: Generate manifest JSON with validation results and deployment metadata"
      - "Phase 6: Wire up dependencies, governance links, memory connections, world model integration"
      - "Phase 7: Validate all files, imports, circular dependencies, governance wiring, deployment readiness"
    deterministic: true
    reproducible: true
    version: 6.0.0
  
  extractor_prompt:
    file: Universal-Extractor-Prompt.md
    purpose: >
      Quick reference prompt for Cursor to invoke the extractor. Summarizes the 7-phase 
      extraction protocol and provides copy-paste instructions for schema → code generation.
    version: 6.0.0
  
  glue_layer:
    file: L9_Universal_Schema_Extractor_Glue_v6.yaml
    purpose: >
      Bridge contract between canonical schemas and the concrete L9 repo layout. 
      Tells Cursor exactly how to map schema fields to real file paths, module imports, 
      test directories, and generated code structure. Eliminates guessing; enforces consistency.
    sections:
      - meta (ID, version, name, description, scope)
      - l9_repo_contract (core paths, role imports for governance, memory, world model, packet protocol)
      - mapping_rules (root path resolution, python generation, docs/config, logs/manifests)
      - codegen_contract (expected files per module type, class patterns, integration requirements)
      - tests_and_validation (test directory structure, minimal test files, assertions)
      - cursor_usage (required inputs, execution plan, success criteria)
    version: 6.0.0

usage_model:
  schema_creation_flow:
    step_1_design: |
      Define the agent/module requirements (role, capabilities, integrations).
      Reference existing schemas (TensorAIOS, Main Agent, PlastOS Adapter) for patterns.
    
    step_2_populate: |
      Use Canonical-Schema-Population-Guide.md to populate every field in 
      Canonical-Schema-Template-v6.0.yaml. Ensure all required sections present.
      Validate schema is syntactically valid YAML.
    
    step_3_create_extractor_map: |
      Define extraction sequence (agent order/dependencies), shared configuration 
      (Redis, PostgreSQL, Neo4j endpoints), post-extraction validation steps, 
      and success criteria in an extractor map YAML.
    
    step_4_invoke_universal_extractor: |
      Provide Cursor with: (a) your completed schema YAML, (b) extractor map YAML, 
      (c) L9_Universal_Schema_Extractor_Glue_v6.yaml, (d) Universal-Schema-Extractor-v6.0.md.
      Cursor parses, validates, and generates all code, tests, docs, manifests.
    
    step_5_validate_and_deploy: |
      Review generated files. Validate imports, run tests, check quality gates 
      (pylint 8.0+, mypy strict, 80% coverage, 90% docstrings). Get governance approval.
      Deploy to staging then production.
  
  optimization_integration:
    how_to_apply_10_point_guide: |
      Reference QPF_10Point_Guide.md for 10 production optimizations:
      1. Schema Versioning (migrations, rollback support)
      2. Parallel Extraction + Caching (5 agents simultaneously)
      3. Dynamic Sub-Agent Creation (spawn agents on demand)
      4. Cross-Domain Learning (transfer patterns across domains)
      5. Anomaly-Driven Agents (auto-generate agents for novel patterns)
      6. Recursive Schema Composition (hierarchical base + sub-schemas)
      7. Extraction Observability (metrics, dashboards, alerts)
      8. Swarm Coordination (flocking, consensus, voting)
      9. Self-Healing Deployments (health checks, auto-recovery)
      10. Drift Detection (schema/manifest mismatches, auto-flag)
      
      For each optimization: (a) understand the concept, (b) identify which applies to your domain,
      (c) update schema to include optimization-specific fields, (d) re-extract,
      (e) deploy with increased confidence and capability.
  
  common_cursor_prompts:
    prompt_1_schema_generation: |
      "I need a new agent for [domain/purpose]. Role: [description]. 
      Integration: [other agents/systems]. Governance: [anchors/rules].
      Using Canonical-Schema-Template-v6.0.yaml and Population-Guide.md,
      generate a complete schema following the pattern from [reference agent]. 
      Validate against all required sections."
    
    prompt_2_code_extraction: |
      "I have schema [name].yaml, extractor map, and glue layer. 
      Using Universal-Schema-Extractor-v6.0.md, extract all code:
      1. Validate schema against quality gates.
      2. Generate 20+ Python modules.
      3. Generate tests (80% coverage).
      4. Generate docs (README, CONFIG, APISPEC, DEPLOYMENT).
      5. Create manifest. Output file tree."
    
    prompt_3_validation_audit: |
      "Check [agent] schema against QualityGateChecklist and 
      Canonical-Schema-Population-Guide. Report passed/failed checks, 
      warnings, and suggested fixes."
    
    prompt_4_extraction_map: |
      "Generate extraction map for these 5 agents: [list].
      Show dependency order, shared configuration, success criteria. 
      Reference L9_Universal_Schema_Extractor_Glue_v6.yaml."
    
    prompt_5_10point_optimization: |
      "Review [agent] and identify which optimizations from 
      QPF_10Point_Guide.md apply. Suggest top 3 with effort/ROI.
      Show schema changes needed for each."

governance:
  space_admin:
    role: L9 System Architect
    responsibilities:
      - Maintain canonical template and population guide
      - Update extractor and glue layer when L9 repo changes
      - Review new schemas before extraction
      - Approve changes to core documents
  
  schema_reviewers:
    role: Domain leads, governance anchors (Igor, Compliance Officer)
    responsibilities:
      - Validate schemas match domain requirements
      - Ensure governance rules properly enforced
      - Approve extraction maps before running
      - Review generated agents for governance compliance
  
  approval_workflow:
    step_1: New schema created and validated
    step_2: Space admin reviews against template
    step_3: Domain lead validates against requirements
    step_4: Governance reviewer checks governance/compliance sections
    step_5: Schema approved for extraction
    step_6: Cursor extracts code
    step_7: QA validates generated code (imports, tests, coverage)
    step_8: Space admin signs off
    step_9: Governance approval requested (Igor, etc.)
    step_10: Deploy to staging/production

recommended_space_description: |
  Quantum Pipeline Factory (QPF) is a schema-driven AI code factory. 
  Upload canonical schemas → extract production-grade Python agents deterministically. 
  Contains: Canonical-Schema-Template-v6.0.yaml, Universal-Schema-Extractor-v6.0.md, 
  glue layer, population guide, 10-point optimization roadmap, Cursor prompts, 
  and Week 1 quickstart. Schema is truth; code is extracted, not written.

changelog:
  - version: 6.0.1
    date: 2025-12-12
    changes: |
      - Tightened core_documents to focus on essential guides
      - Renamed schema_stack and extraction_stack sections with detailed field coverage
      - Aligned naming with Canonical-Schema-Template-v6.0.yaml, 
        Universal-Schema-Extractor-v6.0.md, L9_Universal_Schema_Extractor_Glue_v6.yaml
      - Clarified usage_model with concrete 5-step schema creation flow
      - Added optimization_integration section linking to QPF_10Point_Guide.md
      - Expanded common_cursor_prompts with 5 practical examples
      - Added formal governance section with approval workflow
      - Enhanced recommended_space_description for Perplexity Space settings
      - Documented mandatory vs optional sections in canonical template

  - version: 6.0.0
    date: 2025-12-11
    changes: Initial release
