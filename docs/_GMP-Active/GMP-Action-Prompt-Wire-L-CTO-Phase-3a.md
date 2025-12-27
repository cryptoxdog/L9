Here is a tight, GMP-ready TODO list scoped only to “attach tools and memory to L” (no new design, just wiring and confirmation). All items assume GMP‑L.0–L.4 and GMP‑L.3 approvals are already merged.[1][2][3]

## 1) Confirm L’s capabilities profile

- File: `core/schemas/capabilities.py`[4][1]
  - [ ] Verify `ToolName` includes: `MEMORYSEARCH`, `MEMORYWRITE`, `GMPRUN`, `GITCOMMIT`, `MACAGENTEXECTASK`, `MCPCALLTOOL`, plus any world‑model + substrate tools used in LMEMORYANDTOOLSMANIFEST.[1][4]
  - [ ] Verify there is an `AgentCapabilities` entry for L (agent id `L` or `l-cto`) that marks those tools as allowed and sets any `requires_igor_approval` / risk flags in line with GMP‑L.2 text.[3][1]

## 2) Ensure tool metadata and graph wiring for L

- File: `core/tools/toolgraph.py`[3][4]
  - [ ] Confirm `ToolDefinition` already has `requiresigorapproval: bool = False` and is used by all L tools.[3]
  - [ ] Confirm all L tools (memory search/write, GMP, git, Mac, MCP) each have a `ToolDefinition` instance with:
    - `agentid="L"` (or `l-cto`), correct `category`, `scope` (`internal`/`external`), `risklevel`, and `requiresigorapproval` for high‑risk tools.[1][3]
  - [ ] Confirm `registertool` stores `requiresigorapproval` on the Tool node and `requiresapproval` on the `HASTOOL` relationship, as per GMP‑L.2 exec report.[3]
  - [ ] Confirm `ToolGraph.getltoolcatalog()` returns all of the above tools with correct metadata for L.[5][3]

## 3) Bind L’s tools into the tool registry

- File: `core/tools/registryadapter.py`[4][1]
  - [ ] Verify `ExecutorToolRegistry` has concrete entries for L’s tools, mapping from `ToolName` to callables:  
    - `memory_search` → substrate search implementation.  
    - `memory_write` → substrate write implementation.  
    - `gmprun` → GMP queue tool (already created in prior GMP if present).  
    - `gitcommit` → `runtime/gittool.py` git commit enqueuer with pending status.[2]
    - `macagent.exectask` → Mac / VPS execution tool.  
    - `mcp.calltool` → MCP client wrapper (if implemented).  
  - [ ] Ensure each of these is registered such that `toolregistry.get_approved_tools(agent_id="L")` returns them, filtered by `AgentCapabilities`.[4][1]

## 4) Confirm approval gates apply to L’s high‑risk tools

- File: `core/governance/approvals.py`[2][4]
  - [ ] Confirm `ApprovalManager` methods are present (`approvetask`, `rejecttask`, `isapproved`) and restricted to Igor as per GMP‑L.3.[2]
- File: `core/agents/executor.py`[2][4]
  - [ ] In `dispatch_tool_call`, verify:  
    - Lookup of tool metadata (`ToolGraph.getltoolcatalog()` or equivalent) is used to detect `requiresigorapproval`.  
    - For L tasks, any tool with `requiresigorapproval=True` returns `PENDING_IGOR_APPROVAL` unless `ApprovalManager.isapproved(...)` is true, matching the GMP‑L.3 exec report.[2][3]

## 5) Verify memory tools and audit logging are wired

- File: memory helper module used by the registry (e.g. `core/memory/runtime.py` or dedicated `memorytools.py`, per GMP‑L.4)[1][4]
  - [ ] Confirm implementations of `memorysearch(...)` and `memorywrite(...)` call the substrate via `SubstrateServiceProtocol` and respect the Memory.yaml segments (`governancemeta`, `projecthistory`, `toolaudit`, `sessioncontext`).[1]
- File: `core/agents/executor.py`[4][1]
  - [ ] Confirm that after each tool call, the executor logs to tool audit via `ToolGraph.logtoolcall(...)` with `toolname`, `agentid`, `success`, `duration_ms`, and error fields.[3][1]
  - [ ] Confirm audit entries for memory tools are also written into the `toolaudit` segment of the memory substrate (PacketEnvelope writes), in line with GMP‑L.4 description.[1]

## 6) Confirm L sees and uses tools + memory at runtime

- File: `core/agents/registry.py` or `core/agents/kernelregistry.py` (where `AgentConfig` for L is registered)[4][1]
  - [ ] Verify there is a concrete `AgentConfig` for L whose `capabilities` field is set to the L capabilities profile containing the tools above.[1]
- File: `core/agents/agentinstance.py` / `core/agents/engine.py`[4][1]
  - [ ] Confirm L’s `AgentInstance` receives `ToolBinding`s for all tools returned by `ExecutorToolRegistry` and that these bindings are exposed to the AIOS runtime (tool schemas given to the model).[4][1]
- File: `api/server.py` (or whichever entrypoint now backs `lchat` / `lws`)[1][4]
  - [ ] Confirm `AgentTask` for L uses `agent_id` that matches the config above and is executed via `AgentExecutorService`, not a direct OpenAI call, so L actually has tool + memory access.[1]

These TODOs are ready to be lifted directly into a GMP plan (each bullet can be a TODO ID with file + line anchor once you run a fresh grep on your local tree).
