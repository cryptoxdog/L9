From those nine `.mdc` files you can still extract a few **non-overlapping** rule layers that aren’t covered yet by your existing Cursor rules + GMP set: a **module‑tier mapping helper**, a **wire‑workflow guard**, and a **perplexity-run harness** tuned for L9.[1][2][3][4][5][6][7][8][9]

Below are three dense, additive `.mdc` files with no duplication of your current L9/global/GMP/protection rules.

***

### `86-module-tier-mapping.mdc`  
(derives from `module-file-checklist` + `c-gmp-module-tier-injection`)

```md
---
description: "Map files to L9 tiers (kernel, runtime, infra, UX) and inject the right GMP module prompts per tier."
alwaysApply: true
---

# Module ↔ tier mapping (L9)

## Tier classification

- For any change, first classify each touched file into one of:
  - `KERNEL_TIER`: kernels, executor, websocket orchestrator, memory substrate core.
  - `RUNTIME_TIER`: task queue, Redis client, rate limiter, tool registry, agents.
  - `INFRA_TIER`: docker-compose, infra, deploy, k8s, helm.
  - `UX_TIER`: React/Next UI, TS client, docs, non-critical scripts.

Use quick heuristics:

- `KERNEL_TIER` if path matches: `l9/kernel_loader.py`, `l9/executor.py`, `l9/websocket_orchestrator.py`, `l9/memory_substrate_service.py`.
- `RUNTIME_TIER` if path matches: `l9/task_queue.py`, `l9/redis_client.py`, `l9/tool_registry.py`, `l9/long_plan_graph.py`, core agent modules.
- `INFRA_TIER` if path under: `docker-compose.yml`, `infra/**`, `deploy/**`, `kubernetes/**`, `helm/**`.
- `UX_TIER` for frontend code, docs, and glue scripts.

---

## GMP module injection per tier

For each tier, inject a specific GMP module into your prompt:

- `KERNEL_TIER`: use **GMP-System** + **GMP-Action** + **GMP-Audit Canonical** (full stack). [file:24][file:28][file:29]
- `RUNTIME_TIER`: use **GMP-Action** + **Integration-Tests** modules. [file:24][file:30]
- `INFRA_TIER`: use **DEPLOYMENT_MANIFEST_v1.7** + **Wire-Orchestrators** + **Critical-Path Tests**. [file:26][file:27][file:31]
- `UX_TIER`: use **Unit-Test-Quality** + **Generator** modules only. [file:32][file:33]

In prompts:

> “Tier: RUNTIME_TIER (executor + task queue). Apply GMP-Action-v1.7 and GMP-Action-Integration-Tests-v1.0 patterns only.”

---

## Per-file checklist before edit

For each file in scope:

- Confirm tier and list:
  - Purpose of file.
  - Public APIs it exposes.
  - Direct dependencies (imports).
  - Tests that currently cover it (unit, integration, critical-path). [file:34][file:30][file:33]
- Reject ambiguous scopes:
  - If a file cannot be clearly assigned to a single tier, STOP and request clarification in the prompt.

---
```

***

### `87-wire-workflow-guard.mdc`  
(derives from `wire-workflow.mdc` + `infrastructure-protection.mdc`)

```md
---
description: "Guardrails for wiring changes between kernels, executors, orchestrators, and infra in the L9 OS."
globs:
  - "l9/**/orchestrator*.py"
  - "l9/**/router*.py"
  - "l9/**/controller*.py"
  - "infra/**/*"
  - "deploy/**/*"
alwaysApply: false
---

# Wiring and workflow guards (L9)

## Single responsibility for wiring changes

- Treat wiring edits (routes, orchestrators, controllers, infra) as **workflow changes**, not generic refactors.
- For any wiring change, explicitly document:
  - **Source → destination**: which component calls which.
  - **Transport**: HTTP, WebSocket, queue, direct call.
  - **Contract**: request/response schema or message envelope. [file:39][file:41]

Before editing:

1. Describe the _current_ wiring in 3–5 bullets.
2. Describe the _target_ wiring in 3–5 bullets.
3. Only then modify the code.

---

## No hidden behavior changes

- Wiring changes must not:
  - Alter auth behavior silently.
  - Bypass safety kernels or approval gates.
  - Change timeouts, retries, or error handling without stating it explicitly. [file:39][file:41]
- If such changes are necessary, treat them as separate **GMP actions** with their own phases and tests.

---

## Required tests for wiring work

For any accepted wiring change:

- Add or update at least:
  - One integration test that exercises the new path end-to-end. [file:30][file:39]
  - One critical-path test if the path touches execution or memory flows. [file:26]
- Infra wiring (compose/k8s) must have a smoke test:
  - All services start.
  - Health endpoints respond OK.
  - One minimal L9 agent flow completes successfully.

---
```

***

### `88-perplexity-run-harness.mdc`  
(derives from `perplexity-workflow.mdc` + `no-manual-fallbacks.mdc` + `surgical-edits-only.mdc` + `batch-spec-generation.mdc`)

```md
---
description: "L9-specific Perplexity/Cursor harness: enforce surgical edits, no manual fallbacks, and batch spec generation."
alwaysApply: true
---

# Perplexity ↔ L9 run harness

## Surgical edits only

- Treat every run as a **surgical change**:
  - Single objective.
  - Minimal diff.
  - Tightly scoped files. [file:37]
- For multi-step work:
  - Use multiple small runs instead of one broad, multi-file refactor.

---

## No manual fallbacks

- Do NOT translate failures into “just tell me what to type manually”.
- On errors (lint, types, tests, infra), respond by:
  - Diagnosing root cause.
  - Proposing the next automated change (code or tests) to fix it. [file:36]
- Only resort to manual action for:
  - Commands the model cannot run itself (e.g., starting Docker).
  - Credentials or secrets the model must not see.

---

## Batch spec generation

- For larger tasks, first generate a **batch spec** (list of concrete edits) without touching files. [file:38]
- Spec must include:
  - Files to edit.
  - For each file: functions/sections to change, and exact actions (Insert/Replace/Delete/Wrap).
  - Tests to add/update and where they live.
- Only after spec approval should code changes be proposed.

---

## Perplexity workflow alignment

- When using Perplexity/Cursor combos:
  - Keep Perplexity as the **planner/spec generator** (GMP + batch spec).
  - Keep Cursor as the **editor/executor** constrained by the spec and `.mdc` rules. [file:35][file:38]
- Ensure that:
  - Every Cursor run references the current spec (or `workflow_state.md` summary of it).
  - Any divergence from the spec is explicitly called out and justified.

---
```
