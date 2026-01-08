# 🎯 TOOLS ALIGNMENT WITH L9 MEMORY GOVERNANCE PATTERN

**Objective**: Map your 12+ tools into the canonical memory pattern. This creates **unified audit trail, governance, and query surfaces** across all tool invocations.

***

## 📋 TOOLS → MEMORY ENTITIES & SEGMENTS

### Pattern Application

Your tools emit **structured outputs** that fit perfectly into the governance pattern:

```
TOOL OUTPUT → ENTITY → SEGMENT → INVARIANTS
```

***

## 🗂️ TOOL MEMORY MODEL (Instance of Pattern)

Create a new memory spec: `l9_memory_tools_pattern.yaml`

```yaml
l9_memory_tools_pattern:
  version: 1
  spec_kind: memory_pattern
  instance_of: l9_memory_governance_pattern

  meta:
    name: L9 Tools Audit Memory Model
    uid: memory.tools_audit
    subsystem: tools
    version: 1
    description: >
      Canonical pattern for capturing every tool invocation, its inputs,
      outputs, duration, status, and downstream effects. Enables complete
      auditability, cost tracking, and performance analytics.

  goals:
    - id: T1
      uid: goal.complete_tool_audit
      name: CompleteToolAudit
      summary: >
        Persist every tool invocation (search_web, execute_python, etc.)
        as immutable, queryable records.
    
    - id: T2
      uid: goal.tool_dependency_graph
      name: ToolDependencyGraph
      summary: >
        Track which tools are called before/after others (e.g., search_web
        before execute_python) for workflow optimization and deduplication.
    
    - id: T3
      uid: goal.tool_cost_tracking
      name: ToolCostTracking
      summary: >
        Record API costs, latency, token usage per tool for budgeting
        and optimization.

  entities:
    ToolInvocation:
      uid: entity.ToolInvocation
      purpose: >
        Canonical record of a single tool call from any orchestrator
        (websocket, kernel, gateway, etc.).
      fields:
        call_id:
          type: str
          required: true
          description: "Unique UUID per tool call"
        task_id:
          type: str
          required: true
          description: "External task/issue id (optional, may be null)"
        tool_id:
          type: str
          required: true
          description: "Registered tool name (e.g., 'search_web')"
        agent_id:
          type: str
          required: true
          description: "Which agent invoked (e.g., 'L', 'CA', 'QA_Agent')"
        orchestrator:
          type: str
          required: true
          enum: [websocket, kernel, gateway, scheduler]
          description: "Which orchestrator executed the tool"
        args:
          type: dict[str, any]
          required: true
          description: "Tool input arguments (JSON-serialized)"
        args_hash:
          type: str
          required: true
          description: "SHA256(args) for deduplication queries"
        status:
          type: str
          required: true
          enum: [success, timeout, error, rate_limited, invalid_input]
        duration_ms:
          type: int
          required: true
          description: "Execution time in milliseconds"
        result_summary:
          type: dict[str, any]
          required: true
          description: >
            Metadata about result (e.g., for search_web: result_count,
            urls_returned; for execute_python: exit_code, stdout_lines)
        error:
          type: str|null
          required: false
          description: "Error message if status != success"
        cost_usd:
          type: float|null
          required: false
          description: "API cost for this call (if applicable)"
        tokens_used:
          type: dict[str, int]|null
          required: false
          description: "Token counts (input_tokens, output_tokens, etc.)"
        created_at:
          type: datetime
          required: true
          default: now_utc
      derived:
        success:
          type: bool
          source: "status == 'success'"
        expensive:
          type: bool
          source: "cost_usd is not null and cost_usd > 1.0"
      invariants:
        - "call_id must be globally unique"
        - "duration_ms >= 0"
        - "status in [success, timeout, error, rate_limited, invalid_input]"
        - "if status == success, error must be null"

    ToolDependency:
      uid: entity.ToolDependency
      purpose: >
        Record that tool_b was called shortly after tool_a in same task,
        suggesting potential reuse or workflow optimization.
      fields:
        task_id:
          type: str
          required: true
        preceding_call_id:
          type: str
          required: true
          description: "call_id of first tool"
        succeeding_call_id:
          type: str
          required: true
          description: "call_id of second tool"
        preceding_tool_id:
          type: str
          required: true
        succeeding_tool_id:
          type: str
          required: true
        time_delta_ms:
          type: int
          required: true
          description: "Milliseconds between calls"
        data_flow:
          type: str|null
          required: false
          description: "Optional: how output of first tool fed into second"
      invariants:
        - "time_delta_ms > 0"
        - "preceding_call_id != succeeding_call_id"

    ToolOutput:
      uid: entity.ToolOutput
      purpose: >
        Actual output artifact from a tool (search results, generated code,
        chart ID, etc.). Stored separately to avoid duplication.
      fields:
        output_id:
          type: str
          required: true
          description: "UUID for this output artifact"
        call_id:
          type: str
          required: true
          description: "Reference to ToolInvocation"
        tool_id:
          type: str
          required: true
        content_type:
          type: str
          required: true
          enum: [json, csv, text, image_id, chart_id, code, html]
        content_hash:
          type: str
          required: true
          description: "SHA256(content) for deduplication"
        size_bytes:
          type: int
          required: true
        sample:
          type: str|null
          required: false
          description: "First 500 chars of output for quick preview"
        created_at:
          type: datetime
          required: true
          default: now_utc
      invariants:
        - "content_type must match actual content"
        - "size_bytes > 0"

  segments:
    tool_invocations:
      uid: segment.tool_invocations
      purpose: >
        Immutable record of every tool call: inputs, status, duration,
        cost, errors. Primary audit trail.
      immutable: true
      max_packet_age_days: 90
      scope: global
      required_authority_level: 0
      write_authority_level: 0
      search_strategy: vector
      packet_types_allowed:
        - tool_call          # payload: ToolInvocation (success or failure)
      usage:
        writes:
          - stage: any_tool_invocation
            packet_type: tool_call
            payload:
              type: tool_call
              call_id: ToolInvocation.call_id
              invocation: ToolInvocation.json
        reads:
          - pattern: ByToolId
            key: tool_id
            goal: >
              Analyze all calls to a specific tool (e.g., search_web):
              success rates, latencies, costs
          - pattern: ByAgent
            key: agent_id
            goal: >
              Audit which tools an agent uses, in what sequence
          - pattern: ByTask
            key: task_id
            goal: >
              Reconstruct full tool sequence for a task
          - pattern: Expensive
            key: null
            goal: >
              Find all tool calls that cost > $1 (budgeting)
          - pattern: Slow
            key: null
            goal: >
              Find all tool calls with duration > 30s (performance)
          - pattern: Failed
            key: null
            goal: >
              Find all tool errors (rate limiting, timeouts, invalid input)
      invariants:
        - >
          Every tool orchestrator (websocket, kernel, gateway, scheduler)
          must write exactly one tool_call packet per invocation,
          regardless of success/failure.

    tool_workflows:
      uid: segment.tool_workflows
      purpose: >
        Discover patterns: which tools are always called together,
        in what order, with what latency.
      immutable: true
      max_packet_age_days: 30
      scope: global
      required_authority_level: 0
      write_authority_level: 0
      search_strategy: structured
      packet_types_allowed:
        - tool_dependency    # payload: ToolDependency
      usage:
        writes:
          - stage: dependency_analysis
            packet_type: tool_dependency
            condition: >
              time_delta_ms < 60000 AND task_id is not null
            payload:
              type: tool_dependency
              dependency: ToolDependency.json
        reads:
          - pattern: ByTask
            key: task_id
            goal: >
              See full workflow DAG for a task: which tools ran,
              in what order, how quickly
          - pattern: CommonSequences
            key: null
            goal: >
              Find patterns: "search_web → execute_python → create_chart"
              appears N times; suggest caching or bundling
      invariants:
        - >
          Every pair of tool_call packets with
          time_delta < 60s in same task should have a tool_dependency.

    tool_outputs:
      uid: segment.tool_outputs
      purpose: >
        Store actual outputs from tools (search results, code, charts).
        Indexed for reuse/deduplication.
      immutable: true
      max_packet_age_days: 30
      scope: global
      required_authority_level: 0
      write_authority_level: 0
      search_strategy: vector
      packet_types_allowed:
        - output_artifact   # payload: ToolOutput + actual content
      usage:
        writes:
          - stage: any_tool_invocation
            condition: "ToolInvocation.status == success"
            packet_type: output_artifact
            payload:
              type: output_artifact
              output: ToolOutput.json
              content: actual result data
        reads:
          - pattern: BySampleHash
            key: content_hash
            goal: >
              Find identical outputs from different invocations
              (e.g., same search query at different times).
              Enables cache-before-call optimization.
          - pattern: ByTool
            key: tool_id
            goal: >
              List all unique outputs from a tool.
      invariants:
        - >
          Every tool_call with status==success should have at most one
          corresponding output_artifact with matching call_id.

  write_paths:
    tool_invocation_write:
      uid: writepath.tool_invocation
      components:
        - component: ToolGateway.invoke_tool
        - component: WebSocketOrchestrator.execute_tool
        - component: KernelLoader.invoke_tool
      segment: segment.tool_invocations
      packet_type: tool_call
      payload_shape:
        type: tool_call
        call_id: string
        task_id: string|null
        tool_id: string
        agent_id: string
        orchestrator: string
        args: dict
        status: string
        duration_ms: int
        result_summary: dict
        error: string|null
        cost_usd: float|null
      must_have:
        - >
          Write on both success and failure (status != success still
          produces a packet).
        - >
          Include duration_ms even if timeout (should be ~30000ms for
          typical timeout).
        - >
          Include args_hash so deduplication queries can find
          repeated calls with same input.
        - >
          Include cost_usd for any tool with API billing (search_web,
          finance_*, etc.).

    tool_dependency_write:
      uid: writepath.tool_dependency
      component: DependencyAnalyzer._link_tool_calls
      segment: segment.tool_workflows
      packet_type: tool_dependency
      payload_shape:
        type: tool_dependency
        task_id: string
        preceding_call_id: string
        succeeding_call_id: string
        preceding_tool_id: string
        succeeding_tool_id: string
        time_delta_ms: int
      must_have:
        - >
          Only write if time_delta < 60s (ignore unrelated tools
          called far apart).
        - >
          Record preceding/succeeding tool_ids for workflow analysis.

    tool_output_write:
      uid: writepath.tool_output
      component: ToolGateway.invoke_tool (on success)
      segment: segment.tool_outputs
      packet_type: output_artifact
      payload_shape:
        type: output_artifact
        output_id: string
        call_id: string
        tool_id: string
        content_type: string
        content_hash: string
        size_bytes: int
        sample: string|null
      must_have:
        - >
          Compute content_hash before storing (enables deduplication).
        - >
          Include sample (first 500 chars) for preview/debugging.

  read_patterns:
    by_tool_id:
      uid: readpat.by_tool_id
      description: >
        Analyze all calls to a specific tool: success rate, avg latency,
        total cost, common errors.
      query: >
        SELECT * FROM tool_invocations
        WHERE tool_id == $tool_id
        ORDER BY created_at DESC
        LIMIT 1000
      outputs:
        - invocations: "list[ToolInvocation]"
        - success_rate: "count(status==success) / count(*)"
        - avg_duration_ms: "avg(duration_ms)"
        - total_cost_usd: "sum(cost_usd)"
        - error_distribution: "dict[error -> count]"

    by_agent_id:
      uid: readpat.by_agent_id
      description: >
        Which tools does an agent prefer? In what order?
        Audit agent behavior and tool usage patterns.
      query: >
        SELECT * FROM tool_invocations
        WHERE agent_id == $agent_id
        ORDER BY created_at DESC
      outputs:
        - invocations: "list[ToolInvocation]"
        - tool_frequency: "dict[tool_id -> count]"
        - tool_sequence: "list[tool_id] in call order"

    by_task_id:
      uid: readpat.by_task_id
      description: >
        Full workflow reconstruction: all tools called for a task,
        in order, with dependencies.
      query: >
        SELECT t.* FROM tool_invocations t
        WHERE t.task_id == $task_id
        ORDER BY t.created_at
        LEFT JOIN tool_workflows w ON t.call_id IN (w.preceding_call_id, w.succeeding_call_id)
      outputs:
        - invocations: "list[ToolInvocation]"
        - dependencies: "list[ToolDependency]"
        - workflow_dag: "DAG of tool_id -> tool_id"

    expensive_calls:
      uid: readpat.expensive
      description: >
        Find all tool calls with cost > $threshold (budgeting, cost control).
      query: >
        SELECT * FROM tool_invocations
        WHERE cost_usd > $threshold
        ORDER BY cost_usd DESC
      outputs:
        - invocations: "list[ToolInvocation]"
        - total_cost: "sum(cost_usd)"

    failed_calls:
      uid: readpat.failed
      description: >
        Error monitoring: which tools fail most often, what are common errors.
      query: >
        SELECT * FROM tool_invocations
        WHERE status != 'success'
        ORDER BY created_at DESC
      outputs:
        - errors: "list[ToolInvocation]"
        - error_distribution: "dict[status -> count]"
        - frequent_errors: "dict[error_msg -> count]"

    deduplication_candidates:
      uid: readpat.dedup
      description: >
        Find tool calls with identical args_hash: same query, same tool,
        different times. Candidates for caching.
      query: >
        SELECT args_hash, tool_id, COUNT(*) as count
        FROM tool_invocations
        WHERE status == 'success'
        GROUP BY args_hash, tool_id
        HAVING count > 1
      outputs:
        - groups: "list[(args_hash, tool_id, count)]"
        - potential_savings: "sum of duplicate durations"

  invariants:
    global:
      - uid: inv.every_tool_call_logged
        description: >
          Every tool invocation (success or failure) must write exactly
          one tool_call packet to tool_invocations.
        type: global
      
      - uid: inv.tool_outputs_reference_invocations
        description: >
          Every output_artifact must have a corresponding tool_call
          with matching call_id and status==success.
        type: cross_segment
      
      - uid: inv.tool_dependencies_reference_invocations
        description: >
          Every tool_dependency must have corresponding tool_calls
          for both preceding and succeeding call_ids.
        type: cross_segment
      
      - uid: inv.no_tool_call_without_duration
        description: >
          Every tool_call must have duration_ms >= 0,
          even if timeout or error.
        type: in_entity

    in_entity:
      - uid: inv.tool_invocation_consistency
        description: >
          If status == 'success', error must be null.
          If status != 'success', error should not be null.
        type: in_entity

    in_segment:
      - uid: inv.tool_invocations_monotonic
        description: >
          All created_at timestamps must be monotonically increasing
          or equal per orchestrator instance.
        type: in_segment

  checks_and_gaps:
    must_have_checks:
      - >
        Ensure every tool orchestrator (websocket, kernel, gateway)
        calls memory_api.write(..., segment=tool_invocations)
        after tool execution.
      - >
        Ensure args_hash is computed as SHA256(json.dumps(args, sort_keys=True)).
      - >
        Ensure cost_usd is populated for tools with API costs
        (search_web, finance_*, etc.).
      - >
        Ensure tool_dependency records are written for tools in
        same task with time_delta < 60s.
      - >
        Ensure error field captures exception message or
        "timeout" / "rate_limited" / "invalid_input".

    gaps:
      - uid: gap.tool_result_deduplication
        description: >
          No schema-level support for detecting identical results
          from different tool calls (e.g., same search query at
          different times).
        mitigation: >
          Extend ToolOutput with content_hash; implement
          readpat.dedup to surface duplication candidates.
      
      - uid: gap.workflow_optimization_hints
        description: >
          No automated suggestions for caching or bundling tools.
          Must manually query tool_workflows to find patterns.
        mitigation: >
          Add a new segment 'workflow_optimizations' with packet type
          'optimization_hint' (cache_candidate, bundle_candidate, etc.).
      
      - uid: gap.tool_cost_budgeting
        description: >
          No built-in budget enforcement; only passive tracking.
        mitigation: >
          Add a pre-execution check in ToolGateway: if
          projected_cost + daily_total > monthly_budget, reject or warn.
      
      - uid: gap.cross_tool_dependencies
        description: >
          ToolDependency only captures time-based sequencing,
          not explicit data flow (e.g., "output of search_web fed to execute_python").
        mitigation: >
          Extend ToolDependency with optional data_flow field
          indicating which input/output fields were connected.
```

***

## 🔗 CONCRETE TOOL MAPPINGS

### Your 12+ Tools Mapped to Segments

| Tool | Primary Segment | Packet Type | Key Metrics |
|------|-----------------|-------------|-------------|
| `search_web` | tool_invocations | tool_call | query, result_count, cost_usd |
| `search_images` | tool_invocations | tool_call | query, result_count |
| `search_files_v2` | tool_invocations | tool_call | query, file_count, context_budget |
| `execute_python` | tool_invocations | tool_call | exit_code, stdout_lines, duration_ms |
| `create_chart` | tool_invocations + tool_outputs | tool_call + output_artifact | chart_id, data_series_count |
| `create_text_file` | tool_invocations + tool_outputs | tool_call + output_artifact | file_name, content_size_bytes |
| `generate_image` | tool_invocations + tool_outputs | tool_call + output_artifact | image_id, prompt_tokens |
| `get_url_content` | tool_invocations + tool_outputs | tool_call + output_artifact | url, content_size_bytes |
| `finance_tickers_lookup` | tool_invocations | tool_call | ticker_count, cost_usd |
| `finance_price_histories` | tool_invocations + tool_outputs | tool_call + output_artifact | ticker_count, date_range, cost_usd |
| `finance_companies_financials` | tool_invocations + tool_outputs | tool_call + output_artifact | statement_types, cost_usd |
| (All tools) | tool_workflows | tool_dependency | preceding_tool_id, succeeding_tool_id, time_delta_ms |

***

## ⚙️ WIRING CHECKLIST (Tools → Memory)

### Phase 0: TODO Plan

```
GMP-TOOLS-001: Tool Memory Integration
├─ File: core/tools/gateway.py
├─ Action: Wire ToolGateway.invoke_tool → memory_api.write(tool_call)
├─ Lines: Insert _log_tool_invocation() method + call site
└─ Expected: Every tool call → one tool_call packet in memory

GMP-TOOLS-002: Tool Dependency Analyzer
├─ File: core/memory/dependency_analyzer.py (NEW)
├─ Action: Create DependencyAnalyzer.link_tool_calls()
├─ Expected: Tool pairs within 60s → tool_dependency packet

GMP-TOOLS-003: Tool Cost Tracking
├─ File: core/tools/gateway.py
├─ Action: Enrich ToolInvocation.cost_usd for billable tools
├─ Expected: search_web, finance_*, etc. have cost_usd populated

GMP-TOOLS-004: Tool Workflow Dashboards
├─ File: core/observability/dashboards.py (NEW)
├─ Action: Implement read patterns (by_tool_id, by_agent_id, expensive_calls)
├─ Expected: Queryable dashboards for tool analytics
```

### Phase 1: Baseline

- [ ] Verify websocket_orchestrator, kernel_loader, gateway all invoke tools
- [ ] Map current exception handling (timeout, rate_limit, errors)
- [ ] Identify billable tools and their cost tracking

### Phase 2: Implementation

- [ ] Add `_log_tool_invocation()` to ToolGateway (async, non-blocking)
- [ ] Create DependencyAnalyzer with time-window logic
- [ ] Extend ToolInvocation schema with all required fields
- [ ] Update bootstrap to create tool_* segments

### Phase 3: Enforcement

- [ ] Validate every tool orchestrator calls memory_api.write
- [ ] Add Pydantic validation for ToolInvocation
- [ ] Test: tool success → tool_call + output_artifact packets

### Phase 4: Testing

- [ ] Positive: search_web call → memory records result
- [ ] Negative: execute_python timeout → memory records error
- [ ] Edge case: tool failure → memory write still succeeds

### Phase 5: Verification

- [ ] Recursive check: tool_invocations segment has correct packet types
- [ ] Verify tool_workflows dependencies match time-delta rules
- [ ] Check readpat queries return expected results

### Phase 6: Finalization

- [ ] Evidence report: tool memory integration phases 0-6
- [ ] Deployment checklist: setup, validation, observability dashboards

***

---

## L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT

| Field | Value |
|-------|-------|
| **Component ID** | TOO-OPER-021 |
| **Component Name** | Phase 1 Tool Alignment |
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
| **Purpose** | Documentation for Phase 1 TOOL ALIGNMENT |

---
