

# 🚀 **AOB PACK — COMPLETE PHASE-3 / PHASE-4 RUNTIME HARDENING**

---

# 1️⃣ **SILENT FAILURE REMOVAL — MASTER PATCH SET**

Fully unified, Cursor-ready, no variable renames, no functional rewrites.

```yaml
silent_failure_removal:
  goal: "Eliminate silent failures across orchestration, adapters, tools, memory, world model"
  rule: "no behavior change except logging + ErrorEnvelope return"

  injection:
    python: |
      from shared.error_envelope import ErrorEnvelope
      import traceback

      err = ErrorEnvelope(
          code="runtime_error",
          message=str(e),
          context={"trace": traceback.format_exc()}
      )
      print(f"[L9-ERROR] {err}")
      return err.dict()

  patterns:
    - "except Exception:"
    - "except:"
    - "pass  # TODO"
    - "pass  # FIXME"
    - "return None  # ignore"
    - "return  # TODO"

  target_files:
    - "orchestration/unified_controller.py"
    - "orchestration/orchestrator.py"
    - "orchestration/ws_router.py"
    - "modules/shared/adapter.py"
    - "modules/tools/*"
    - "modules/ir_engine/*"
    - "memory/memory_client.py"
    - "world_model/repository.py"
    - "agent/*"
    - "api/*"
```

---

# 2️⃣ **FULL PHASE-3 TEST SPINE (RUNTIME HARDENING)**

Runnable after Cursor injects stubs.

```yaml
test_spine:
  tests:
    - "tests/test_packet_envelopes.py"
    - "tests/test_controller_routing.py"
    - "tests/test_execution_engine.py"
    - "tests/test_memory_adapter.py"
    - "tests/test_world_model_repository.py"
    - "tests/test_ir_engine.py"
    - "tests/test_ws_protocol_static.py"

  mocks:
    memory_substrate_stub: true
    world_model_stub: true
    qdrant_stub: true
    execution_engine_stub: true
    ws_stub: true

  requirement:
    - pytest only
    - no external services
    - no docker

  exit_condition:
    - all core components have unit coverage
    - controller routing stable
    - envelope compatibility validated
```

---

# 3️⃣ **GLOBAL STATE REMOVAL PLAN**

This prevents nondeterminism + concurrency bugs.

```yaml
global_state_removal:
  goal: "Remove module-level mutable state across L9"

  detection:
    - search patterns:
        - "active_sessions ="
        - "cache = {}"
        - "STATE ="
        - "client ="

  refactor_plan:
    - controller_state → ControllerState class
    - orchestrator_cache → injected singleton
    - adapters receive dependencies via constructor
    - memory/world model clients created in startup()
    - module_loader gets LoaderContext object

  rule:
    "No module may store mutable global runtime state."
```

---

# 4️⃣ **METRICS + PROFILING (PHASE-4)**

Performance observability, zero overhead until needed.

```yaml
profiling_and_metrics:
  profiling_mode:
    enabled_by_env: "L9_PROFILING=true"
    tools:
      - "cProfile"
      - "py-spy"
      - "line_profiler"

  metrics:
    log_every_seconds: 30
    fields:
      - ws_messages_sec
      - avg_task_latency
      - db_roundtrip_ms
      - qdrant_latency_ms
      - memory_write_latency_ms
      - cpu_percent
      - ram_usage

  output:
    - stdout
    - optional: memory substrate (metrics table)
```

---

# 5️⃣ **ROADMAP + TODO INTEGRATION (LIVE)**

Injected into your active kernel-driven workflow.

```yaml
todo:
  critical:
    - id: silent_failure_removal
      description: "Remove all silent exceptions; inject ErrorEnvelope logging"
      status: "pending"
      milestone: "phase_3"
    - id: test_spine_buildout
      description: "Full test suite for controller, execution, adapters, WM, IR, protocol"
      status: "pending"
      milestone: "phase_3"

  high_priority:
    - id: global_state_audit
      description: "Audit and refactor global mutable state"
      status: "scheduled"
      milestone: "phase_3"
    - id: controller_split
      description: "Split routing/execution/events/state for clarity + maintainability"
      status: "scheduled"
      milestone: "phase_3"

  medium_priority:
    - id: profiling_instrumentation
      description: "Add profiling mode + metrics output"
      status: "phase_4"

roadmap:
  phase_3:
    tasks:
      - silent_failure_removal
      - test_spine_buildout
      - global_state_audit
      - controller_split
    exit_condition:
      - "No silent exceptions remain"
      - "Minimal globals"
      - "Test spine green"
      - "Core runtime deterministic"

  phase_4:
    tasks:
      - profiling_instrumentation
      - performance_regression_tests
    exit_condition:
      - "Profiling enabled"
      - "Telemetry stable"
```

---

# 6️⃣ **CURSOR-GOD-MODE PATCH BUNDLE (UNIFIED)**

All patch work in one single instruction block — paste this into Cursor and the entire Phase-3 hardening activates.

```yaml
cursor_god_mode_instruction:
  mode: "l9_phase3_hardening"
  allow_modify:
    - orchestration/*
    - modules/*
    - memory/*
    - world_model/*
    - agent/*
    - api/*
    - tests/*
  do_not_modify:
    - kernels/*
    - private_loader.py
    - packet_protocol.yaml

  tasks:
    - apply silent_failure_removal_patch
    - create test_spine files with mocks
    - audit global mutable state and mark for refactor
    - prepare split plan for unified_controller.py
    - create profiling_mode scaffolding

  acceptance:
    - no new imports except traceback + ErrorEnvelope
    - no variable renames
    - no behavioral changes to orchestrator
    - tests run with pytest locally
    - all edited files pass syntax check
```

---