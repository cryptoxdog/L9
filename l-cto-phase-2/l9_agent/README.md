# L9 Agent - High-Agency Autonomy System

## Overview

The `l9_agent` module implements Phase 5 of the L9 architecture: **High-Agency Autonomy**. This module provides the cognitive infrastructure for the L agent to think clearly, act boldly, improve continuously, serve with foresight, and align with the mission.

## Architecture

The L9 agent cognitive architecture is organized into several interconnected systems:

### Core Cognitive Systems

1. **Value Alignment** - Ensures actions align with core values
2. **Motivation Core** - Manages desire, will, and persistence
3. **Emotion System** - Tracks and regulates emotional states
4. **Belief System** - Models and updates beliefs
5. **Trust System** - Manages trust scores for partners/users
6. **Foresight Engine** - Plans and predicts outcomes
7. **Judgment System** - Makes decisions with dual-process thinking

### Advanced Systems

8. **Theory of Mind** - Models partner beliefs and intentions
9. **Multi-Agent Coordination** - Enables collaboration with other agents
10. **Negotiation** - Handles bargaining and compromise
11. **Conflict Resolution** - Detects and resolves conflicts
12. **Partner Intent Modeling** - Infers goals through Bayesian inference
13. **Belief Calibration** - Calibrates confidence in beliefs

## Module Structure

```
l9_agent/
├── __init__.py
├── README.md
│
├── Core Modules
├── value_alignment.py          # Value alignment engine
├── value_tests.py              # Value alignment tests
├── desire_engine.py            # Desire tracking
├── will_engine.py              # Will/commitment
├── persistence_engine.py       # Persistence logic
├── goal_commitment.py          # Goal commitment tracker
├── desire_tests.py             # Motivation tests
├── trust_model.py              # Trust score tracking
├── trust_engine.py             # Trust update logic
├── trust_hooks.py              # Trust integration hooks
├── trust_visualization.py      # Trust visualization
├── trust_tests.py              # Trust tests
│
├── Subsystem Modules
├── judgment_core/              # Judgment and decision making
├── theory_of_mind/             # Partner modeling
├── multi_agent_core/           # Multi-agent coordination
├── negotiation/                # Negotiation engine
├── conflict_resolution/        # Conflict resolution
├── partner_intent_model/       # Bayesian goal inference
├── belief_calibration/         # Belief calibration
├── hybrid_graph/               # Knowledge graph
└── sandbox/                    # Safe execution environment
```

## Configuration

Configuration files are located in `/config/`:

- `core_values.yaml` - Core values and weights
- `desire_profile.yaml` - Motivation parameters
- `trust_config.yaml` - Trust modeling configuration
- `l9_agent/` - Additional module-specific configs

## Integration

### State Manager Integration

The `l9_agent` modules require updates to `state_manager.py`:

```python
# Value alignment tracking
self.value_alignment_history = []
self.current_value_alignment = 0.0

# Motivation tracking
self.active_goals = {}

# Trust tracking
self.trust_model = TrustModel(initial=0.5, decay=0.01)
```

### Reflection Engine Hooks

Add to `reflection_engine.py`:

```python
from l9_agent.value_alignment import ValueAlignmentEngine

# Initialize
self.value_engine = ValueAlignmentEngine()

# In reflection loop
score = self.value_engine.score_action(action_tags)
self.state.record_value_alignment(score)
```

### Foresight Engine Hooks

Add to `foresight_engine.py`:

```python
# Filter actions by value alignment
for action in candidates:
    alignment_score = self.value_engine.score_action(action.tags)
    if alignment_score < threshold:
        continue  # Skip misaligned actions
```

## Testing

Run all tests:

```bash
cd /home/ubuntu/L9
python3 -m pytest l9_agent/
```

Run specific test suites:

```bash
python3 l9_agent/value_tests.py
python3 l9_agent/desire_tests.py
python3 l9_agent/trust_tests.py
```

## Usage Examples

### Value Alignment

```python
from l9_agent.value_alignment import ValueAlignmentEngine

engine = ValueAlignmentEngine()
score = engine.score_action(["trust", "coherence", "truthfulness"])
explanation = engine.explain_score(["trust", "coherence"])
```

### Motivation Core

```python
from l9_agent.desire_engine import DesireEngine
from l9_agent.will_engine import WillEngine
from l9_agent.persistence_engine import PersistenceEngine
from l9_agent.goal_commitment import GoalCommitmentTracker

desire = DesireEngine()
will = WillEngine()
persist = PersistenceEngine({"activation": 0.6, "abandonment": 0.2})

tracker = GoalCommitmentTracker(desire, will, persist)

# Register and track a goal
desire.register_goal("complete_project")
desire.reinforce("complete_project", 0.3)
should_continue = tracker.update_goal("complete_project")
```

### Trust Modeling

```python
from l9_agent.trust_model import TrustModel
from l9_agent.trust_engine import TrustEngine

trust = TrustModel(initial=0.5)
config = {"reinforce_step_positive": 0.1, "reinforce_step_negative": 0.15}

class MockState:
    def __init__(self):
        self.trust_model = trust

engine = TrustEngine(MockState(), config)
engine.on_success()  # Increase trust
engine.on_failure()  # Decrease trust
```

## Development Status

### Completed ✅
- Value Alignment System
- Motivation Core (Desire + Will + Persistence)
- Trust Modeling System
- Directory structure
- Configuration files
- Test suites

### In Progress 🚧
- Emotion System
- Belief System
- Foresight Engine Phase 2
- Judgment Core
- Decision Controller

### Planned 📋
- Theory of Mind
- Multi-Agent Core
- Negotiation Engine
- Partner Intent Model
- Belief Calibration

## God-Mode Cursor Prompt (CGMP)

The implementation follows a phased execution model:

1. **Phase -1**: Analysis & Planning
2. **Phase 0**: Baseline Confirmation
3. **Phase 1**: Primary Implementation
4. **Phase 2**: Enforcement Implementation
5. **Phase 3**: System Guards
6. **Phase 4**: Second Pass Validation
7. **Phase 5**: Final Sanity Sweep

See the chat transcript for the complete CGMP specification.

## Contributing

When adding new modules:

1. Follow the existing module structure
2. Include comprehensive docstrings
3. Add configuration files to `/config/`
4. Create test files with `_tests.py` suffix
5. Update this README
6. Ensure integration points are documented

## License

Part of the L9 OS project.

## Contact

For questions or issues, refer to the L9 project documentation.
