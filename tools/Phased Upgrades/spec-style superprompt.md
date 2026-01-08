l9_gap_analysis_superprompt:
  version: 3
  spec_kind: analysis_pattern

  description: >
    Reusable prompt pattern to generate a deep gap analysis and
    frontier-lab comparison for any L9 subsystem (memory, tools,
    orchestration, auth, agents, etc.), expressed as a structured spec,
    suitable for continuous improvement loops.

  inputs:
    component_name: string
    component_brief: string
    l9_specs_or_files:
      type: string
      description: >
        High-level description of relevant L9 specs/files for this component
        (e.g., segments, entities, workflows, tools, agents, configs).

  frontier_targets:
    labs:
      # Frontier model / infra labs
      - OpenAI
      - Google DeepMind
      - Anthropic
      - Meta (FAIR)
      - Microsoft
      - Amazon (AWS)
      - xAI
      - Mistral AI

      # Frontier autonomous coding / agentic product companies
      - Cognition AI
      - AnySphere
      - Reflection AI
      - Blitzy

    focus_areas:
      - memory_architecture
      - agent_orchestration
      - tool_integration
      - production_readiness

  task:
    goal: >
      Analyze the given L9 component and produce a frontier-grade gap
      analysis, component synthesis, and scalability roadmap compared to
      the listed labs/companies.

    required_outputs:
      - executive_summary
      - component_overview
      - frontier_comparisons
      - gap_matrix
      - priority_matrix
      - component_synthesis
      - scalability_matrix
      - roadmap
      - metrics_and_readiness

  output_format:
    type: markdown
    sections:

      - name: Executive Summary
        required: true
        content: >
          1–2 paragraphs (4–8 sentences each) answering:
          - Where this L9 component sits vs the listed labs/companies
            (approximate % parity).
          - Main structural strengths and design advantages.
          - Critical gaps that block production/enterprise use and why
            they matter in real workloads.

      - name: Component Overview
        required: true
        content: >
          1–2 paragraphs (4–8 sentences each) describing:
          - The role of this component inside L9.
          - Key responsibilities, invariants, and external dependencies.
          - How it currently interacts with memory, tools, agents,
            and orchestration.

      - name: Frontier Comparisons
        required: true
        content: >
          Group the labs/companies into:
          - (a) Foundation/model/infra platforms (OpenAI, Google DeepMind,
            Anthropic, Meta, Microsoft, AWS, xAI, Mistral),
          - (b) Autonomous coding/agentic product companies
            (Cognition AI, AnySphere, Reflection AI, Blitzy).
          For each group and each relevant lab/company:
          - Provide 1–2 paragraphs (4–8 sentences max) with deeper insight
            into how they solve similar problems (architecture, patterns,
            trade-offs).
          - Include at least one markdown table per group:
            Feature | L9 | Frontier | Gap Impact (Critical/Medium/Minor).

      - name: Gap Matrix
        required: true
        content: >
          One dense markdown table summarizing ALL identified gaps:
          Columns:
          - Gap
          - Category (memory_architecture | agent_orchestration |
            tool_integration | production_readiness)
          - Impact_if_not_fixed (1–2 lines)
          - Severity (Critical/Medium/Minor)
          - Estimated_effort_weeks.

      - name: Priority Matrix
        required: true
        content: >
          One markdown table focusing ONLY on the highest-impact gaps:
          Columns:
          - Priority (P0, P1, P2)
          - Gap
          - Impact_if_not_fixed
          - Effort_weeks
          - Frontier_reference (which lab/company shows the target state).

      - name: Component Synthesis
        required: true
        content: >
          2–3 paragraphs (4–8 sentences each) synthesizing *which*
          frontier components and patterns to benchmark and integrate
          for maximum impact:
          - Identify specific features/modules from the labs/companies
            that, if emulated or integrated, would most improve this L9
            component.
          - Discuss whether these components **complement** each other or
            **overlap**, and where there is potential duplication.
          - Propose how they could be **combined** into a coherent design
            that optimizes output and maximizes benefit for L9
            (e.g., “Mem0-style consolidation + Bedrock-style tool audit
            + Claude-style subagents”).

      - name: Scalability Matrix
        required: true
        content: >
          REQUIRED: Provide both a table and short narrative.
          Table columns:
          - Dimension (scale axis: users, tasks, repos, sessions, tools, models)
          - What_this_enables_now
          - What_to_patch (short-term fixes or mitigations)
          - What_to_build_next_for_maximum_impact
            (defined as: creates leverage for scalability).
          After the table, add 1–2 paragraphs (4–8 sentences each) that:
          - Explain how the proposed changes unlock new scale regimes
            (e.g., more concurrent agents, longer sessions, bigger codebases).
          - List the **next 3 things to build in priority order** that create
            the most scalability leverage, with a one-sentence rationale
            for each.

      - name: Roadmap
        required: true
        content: >
          A phased roadmap tailored to this component:
          - 3–6 phases (Phase 1..N) over ~3–9 months.
          - For each phase: time window in weeks, goals, concrete
            deliverables, and success criteria.
          - Explicitly align phases to closing P0/P1 gaps and to the
            “next 3 things” from the Scalability Matrix.

      - name: Metrics & Readiness
        required: true
        content: >
          A markdown table of 5–10 concrete metrics:
          Columns:
          - Metric
          - Current_L9
          - Frontier_Target
          - L9_as_percent_of_Frontier (rough %).
          Then 1–2 paragraphs (4–8 sentences each) giving a readiness
          verdict:
          - What this component IS ready for.
          - What it is NOT yet ready for.
          - The minimal set of changes required to declare it
            “production-ready for scaled use.”

  style:
    constraints:
      - "Use 1–2 paragraphs per narrative section, 4–8 sentences each, with deeper analysis rather than bullet-point summaries."
      - "Always reference specific labs/companies from the configured list (no extras)."
      - "Avoid duplicates in lab/company lists and in feature comparisons."
      - "Keep tables dense and implementation-focused, not marketing-style."
      - "Assume the reader is a senior architect; be concise but analytically rich."

  invocation_example: |
    You are an expert AI systems architect.
    Use the `l9_gap_analysis_superprompt` pattern.

    component_name: "L9 Tool Gateway + Tool Memory Integration"
    component_brief: >
      Tool orchestration layer that routes agent tool calls (search_web, execute_python,
      finance_*, create_chart, etc.) and will be wired into the L9 memory system
      (tool_audit, project_history, session_context).

    l9_specs_or_files: >
      Treat the existing L9 memory governance spec and tool catalog as the current baseline.
      Analyze how this component compares to OpenAI, Google DeepMind, Anthropic, Meta (FAIR),
      Microsoft, Amazon (AWS), xAI, Mistral AI, Cognition AI, AnySphere, Reflection AI, and Blitzy.

---

## L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT

| Field | Value |
|-------|-------|
| **Component ID** | TOO-OPER-004 |
| **Component Name** | Spec Style Superprompt |
| **Module Version** | 1.0.0 |
| **Created At** | 2026-01-08T03:17:26Z |
| **Created By** | L9_DORA_Injector |
| **Layer** | operations |
| **Domain** | tools |
| **Type** | schema |
| **Status** | active |
| **Governance Level** | medium |
| **Compliance Required** | True |
| **Audit Trail** | True |
| **Purpose** | Documentation for spec style superprompt |

---
