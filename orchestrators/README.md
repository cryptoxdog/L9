# L9 Orchestrators

> Agent coordination patterns for the L9 platform.

## Overview

Orchestrators are modular coordination patterns that manage agent workflows, tool execution, reasoning chains, and system evolution.

## Directory Structure

```
orchestrators/
├── action_tool/      # Tool execution orchestration
├── evolution/        # Self-improvement & adaptation
├── memory/           # Memory management & housekeeping
├── meta/             # Meta-reasoning & reflection
├── reasoning/        # Inference chain coordination
├── research_swarm/   # Multi-agent research patterns
└── world_model/      # World model update coordination
```

## Orchestrator Pattern

Each orchestrator follows a consistent structure:

```
<orchestrator>/
├── __init__.py       # Module exports
├── interface.py      # Abstract interface / protocol
├── orchestrator.py   # Main orchestrator implementation
└── *.py              # Additional components
```

## Available Orchestrators

### action_tool
Tool execution with validation and error handling.

### evolution
Self-improvement via feedback loops and pattern adaptation.

### memory
Memory housekeeping, garbage collection, and optimization.

### meta
Meta-reasoning for strategy selection and reflection.

### reasoning
Inference chain coordination with confidence tracking.

### research_swarm
Multi-agent research with convergence and synthesis.

### world_model
World model updates, scheduling, and causal inference.

## Usage

```python
from orchestrators.reasoning import ReasoningOrchestrator
from orchestrators.memory import MemoryOrchestrator

# Initialize orchestrators
reasoning = ReasoningOrchestrator(config)
memory = MemoryOrchestrator(repository)

# Run coordination
result = await reasoning.run(context)
await memory.housekeep()
```

## Interface Contract

All orchestrators implement:

```python
class OrchestratorInterface(Protocol):
    async def run(self, context: Any) -> Any: ...
    async def health_check(self) -> dict: ...
```

---

*L9 Platform — Orchestrators Module*

